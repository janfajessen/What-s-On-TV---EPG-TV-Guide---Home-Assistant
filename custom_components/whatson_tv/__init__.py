"""What's On TV EPG — integración mundial de programación de TV para Home Assistant."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import timedelta

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.event import async_track_time_interval

from .const import CONF_EPG_URL, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL, DOMAIN
from .coordinator import EPGCoordinator

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["sensor"]

_OWNER_KEY  = f"{DOMAIN}_owner_entry"
_TIMER_KEY  = f"{DOMAIN}_global_timer"

SERVICE_ADD_WATCH    = "add_watch"
SERVICE_REMOVE_WATCH = "remove_watch"

SCHEMA_ADD_WATCH = vol.Schema({
    vol.Required("keyword"):        cv.string,
    vol.Required("notify_service"): cv.string,
    vol.Optional("hours_before", default=24): vol.All(vol.Coerce(float), vol.Range(min=0.25, max=168)),
    vol.Optional("match", default="word"): vol.In(["contains", "word", "exact"]),
})
SCHEMA_REMOVE_WATCH = vol.Schema({
    vol.Required("watch_id"): cv.string,
})


@dataclass
class WhatsonTVData:
    coordinator: EPGCoordinator


type WhatsonTVConfigEntry = ConfigEntry[WhatsonTVData]


async def async_setup_entry(hass: HomeAssistant, entry: WhatsonTVConfigEntry) -> bool:
    url           = entry.data[CONF_EPG_URL]
    scan_interval = entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

    coordinator = EPGCoordinator(hass, url, scan_interval)

    # Solo el primer entry en cargar gestiona watches y el timer
    is_owner = _OWNER_KEY not in hass.data.get(DOMAIN, {})
    if is_owner:
        await coordinator.load_watches_from_storage()
        hass.data.setdefault(DOMAIN, {})[_OWNER_KEY] = entry.entry_id

    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = WhatsonTVData(coordinator=coordinator)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Registrar servicios y timer global (solo una vez)
    if not hass.services.has_service(DOMAIN, SERVICE_ADD_WATCH):

        async def handle_add_watch(call: ServiceCall) -> None:
            owner_coord = _get_owner_coordinator(hass)
            if not owner_coord:
                return
            watch = await owner_coord.add_watch(
                keyword        = call.data["keyword"],
                notify_service = call.data["notify_service"],
                hours_before   = call.data.get("hours_before", 24),
                match          = call.data.get("match", "word"),
            )
            # Refrescar TODOS los coordinators
            for e in hass.config_entries.async_entries(DOMAIN):
                try:
                    e.runtime_data.coordinator.async_set_updated_data(
                        e.runtime_data.coordinator.data)
                except Exception:
                    pass
            hass.bus.async_fire(f"{DOMAIN}_watch_added", watch)

        async def handle_remove_watch(call: ServiceCall) -> None:
            owner_coord = _get_owner_coordinator(hass)
            if not owner_coord:
                return
            removed = await owner_coord.remove_watch(call.data["watch_id"])
            if removed:
                # Refrescar TODOS los coordinators para que sus sensores se actualicen
                for e in hass.config_entries.async_entries(DOMAIN):
                    try:
                        e.runtime_data.coordinator.async_set_updated_data(
                            e.runtime_data.coordinator.data)
                    except Exception:
                        pass

        hass.services.async_register(DOMAIN, SERVICE_ADD_WATCH,    handle_add_watch,    SCHEMA_ADD_WATCH)
        hass.services.async_register(DOMAIN, SERVICE_REMOVE_WATCH, handle_remove_watch, SCHEMA_REMOVE_WATCH)

        # Timer global: comprueba watches en todos los coordinators cada 5 minutos
        @callback
        def _timer_tick(_now=None):
            hass.async_create_task(_run_global_check())

        async def _run_global_check():
            for e in hass.config_entries.async_entries(DOMAIN):
                try:
                    coord = e.runtime_data.coordinator
                    await coord.check_watches_now()
                except Exception as err:
                    _LOGGER.debug("Error en timer global: %s", err)

        unsub = async_track_time_interval(hass, _timer_tick, timedelta(minutes=5))
        hass.data[DOMAIN][_TIMER_KEY] = unsub
        _LOGGER.debug("Timer global de watches registrado")

    return True


def _get_owner_coordinator(hass: HomeAssistant) -> EPGCoordinator | None:
    """Obtener el coordinator dueño (el que gestiona el storage de watches)."""
    owner_id = hass.data.get(DOMAIN, {}).get(_OWNER_KEY)
    if not owner_id:
        return None
    for entry in hass.config_entries.async_entries(DOMAIN):
        if entry.entry_id == owner_id:
            try:
                return entry.runtime_data.coordinator
            except AttributeError:
                return None
    return None


async def async_unload_entry(hass: HomeAssistant, entry: WhatsonTVConfigEntry) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    domain_data = hass.data.get(DOMAIN, {})
    owner_id    = domain_data.get(_OWNER_KEY)

    # Si esta entrada era la dueña, transferir propiedad o limpiar
    if owner_id == entry.entry_id:
        remaining = [
            e for e in hass.config_entries.async_entries(DOMAIN)
            if e.entry_id != entry.entry_id and e.state.recoverable
        ]
        if remaining:
            # Transferir propiedad al siguiente entry
            domain_data[_OWNER_KEY] = remaining[0].entry_id
        else:
            # Último entry: limpiar todo
            unsub = domain_data.pop(_TIMER_KEY, None)
            if unsub:
                unsub()
            domain_data.pop(_OWNER_KEY, None)
            hass.services.async_remove(DOMAIN, SERVICE_ADD_WATCH)
            hass.services.async_remove(DOMAIN, SERVICE_REMOVE_WATCH)

    return unloaded
    