"""What's On TV EPG — integración mundial de programación de TV para Home Assistant."""

from __future__ import annotations

import logging
import voluptuous as vol
from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .const import CONF_EPG_URL, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL, DOMAIN
from .coordinator import EPGCoordinator

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["sensor"]

# Clave para rastrear qué entrada "posee" los servicios globales
_SERVICES_OWNER_KEY = f"{DOMAIN}_services_owner"

@dataclass
class WhatsonTVData:
    coordinator: EPGCoordinator


type WhatsonTVConfigEntry = ConfigEntry[WhatsonTVData]

SERVICE_ADD_WATCH    = "add_watch"
SERVICE_REMOVE_WATCH = "remove_watch"

SCHEMA_ADD_WATCH = vol.Schema({
    vol.Required("keyword"):        cv.string,
    vol.Required("notify_service"): cv.string,
    vol.Optional("hours_before", default=24): vol.All(vol.Coerce(int), vol.Range(min=1, max=168)),
})
SCHEMA_REMOVE_WATCH = vol.Schema({
    vol.Required("watch_id"): cv.string,
})


async def async_setup_entry(hass: HomeAssistant, entry: WhatsonTVConfigEntry) -> bool:
    url           = entry.data[CONF_EPG_URL]
    scan_interval = entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

    coordinator = EPGCoordinator(hass, url, scan_interval)
    await coordinator.async_load_watches()
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = WhatsonTVData(coordinator=coordinator)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Registrar servicios solo si no están ya registrados (primera entrada)
    if not hass.services.has_service(DOMAIN, SERVICE_ADD_WATCH):
        # La primera entrada en cargar se convierte en "dueña" de los servicios
        hass.data.setdefault(DOMAIN, {})[_SERVICES_OWNER_KEY] = entry.entry_id

        # Los servicios usan el coordinador de la primera entrada para watches
        # (las watches son preferencias globales del usuario, no por fuente EPG)
        async def handle_add_watch(call: ServiceCall) -> None:
            watch = await coordinator.add_watch(
                keyword        = call.data["keyword"],
                notify_service = call.data["notify_service"],
                hours_before   = call.data.get("hours_before", 24),
            )
            # Notificar a todos los listeners del coordinador (actualiza EPGWatchesSensor)
            coordinator.async_set_updated_data(coordinator.data)
            hass.bus.async_fire(f"{DOMAIN}_watch_added", watch)

        async def handle_remove_watch(call: ServiceCall) -> None:
            removed = await coordinator.remove_watch(call.data["watch_id"])
            if removed:
                coordinator.async_set_updated_data(coordinator.data)
                hass.bus.async_fire(f"{DOMAIN}_watch_removed", {"watch_id": call.data["watch_id"]})

        hass.services.async_register(DOMAIN, SERVICE_ADD_WATCH,    handle_add_watch,    SCHEMA_ADD_WATCH)
        hass.services.async_register(DOMAIN, SERVICE_REMOVE_WATCH, handle_remove_watch, SCHEMA_REMOVE_WATCH)
        _LOGGER.debug("Servicios %s registrados por entrada %s", DOMAIN, entry.entry_id)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: WhatsonTVConfigEntry) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    # Solo eliminar servicios si esta entrada es la dueña Y es la última en descargarse
    owner = hass.data.get(DOMAIN, {}).get(_SERVICES_OWNER_KEY)
    if owner == entry.entry_id:
        # Comprobar si quedan otras entradas activas
        other_entries = [
            e for e in hass.config_entries.async_entries(DOMAIN)
            if e.entry_id != entry.entry_id and e.state.recoverable
        ]
        if not other_entries:
            hass.services.async_remove(DOMAIN, SERVICE_ADD_WATCH)
            hass.services.async_remove(DOMAIN, SERVICE_REMOVE_WATCH)
            hass.data.get(DOMAIN, {}).pop(_SERVICES_OWNER_KEY, None)
            _LOGGER.debug("Servicios %s eliminados", DOMAIN)

    return unloaded
