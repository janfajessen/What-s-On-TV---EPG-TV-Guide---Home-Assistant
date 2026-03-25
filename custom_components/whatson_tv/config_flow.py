"""Config Flow para What's On TV — compatible HA 2026."""

from __future__ import annotations

import gzip
import logging
from typing import Any
from xml.etree import ElementTree as ET

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlowWithReload,
)
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import (
    CONF_CHANNELS,
    CONF_EPG_SOURCE,
    CONF_EPG_URL,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_SOURCE,
    DOMAIN,
    EPG_SOURCES,
)

_LOGGER = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _fetch_channels(hass, url: str) -> dict[str, str]:
    """Descarga el EPG y devuelve {channel_id: display_name}."""
    session = async_get_clientsession(hass)
    async with session.get(url, timeout=aiohttp.ClientTimeout(total=120)) as resp:
        resp.raise_for_status()
        raw = await resp.read()

    def _parse(raw_bytes: bytes) -> dict[str, str]:
        if raw_bytes[:2] == b"\x1f\x8b":
            raw_bytes = gzip.decompress(raw_bytes)
        root = ET.fromstring(raw_bytes.decode("utf-8", errors="replace"))
        return {
            ch.get("id"): name_el.text.strip()
            for ch in root.findall("channel")
            if (ch_id := ch.get("id"))
            and (name_el := ch.find("display-name")) is not None
            and name_el.text
        }

    return await hass.async_add_executor_job(_parse, raw)


def _channel_options(channels: dict[str, str]) -> list[SelectOptionDict]:
    return [
        SelectOptionDict(value=k, label=f"{v}  [{k}]")
        for k, v in sorted(channels.items(), key=lambda x: x[1].lower())
    ]


def _source_options() -> list[SelectOptionDict]:
    return [
        SelectOptionDict(value=k, label=v["name"])
        for k, v in EPG_SOURCES.items()
    ]


def _interval_selector() -> NumberSelector:
    return NumberSelector(
        NumberSelectorConfig(min=1, max=24, step=1, mode=NumberSelectorMode.BOX)
    )


# ---------------------------------------------------------------------------
# Config Flow principal
# ---------------------------------------------------------------------------

class WhatsonTVConfigFlow(ConfigFlow, domain=DOMAIN):
    """Config flow — 3 pasos: fuente → (url personalizada) → canales."""

    VERSION = 1

    def __init__(self) -> None:
        self._source: str = DEFAULT_SOURCE
        self._url: str = ""
        self._scan_interval: int = DEFAULT_SCAN_INTERVAL
        self._channels: dict[str, str] = {}

    # -- Paso 1: elegir fuente --

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            self._source = user_input[CONF_EPG_SOURCE]
            self._scan_interval = int(user_input[CONF_SCAN_INTERVAL])

            if self._source == "custom":
                return await self.async_step_custom_url()

            self._url = (
                EPG_SOURCES[self._source].get("url_gz")
                or EPG_SOURCES[self._source]["url"]
            )
            try:
                self._channels = await _fetch_channels(self.hass, self._url)
            except aiohttp.ClientError:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Error inesperado descargando EPG")
                errors["base"] = "unknown"
            else:
                if not self._channels:
                    errors["base"] = "no_channels"
                else:
                    return await self.async_step_channels()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_EPG_SOURCE, default=DEFAULT_SOURCE): SelectSelector(
                    SelectSelectorConfig(options=_source_options(), mode=SelectSelectorMode.LIST)
                ),
                vol.Required(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): _interval_selector(),
            }),
            errors=errors,
        )

    # -- Paso opcional: URL personalizada --

    async def async_step_custom_url(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            self._url = user_input[CONF_EPG_URL].strip()
            try:
                self._channels = await _fetch_channels(self.hass, self._url)
            except Exception:
                errors["base"] = "cannot_connect"
            else:
                if not self._channels:
                    errors["base"] = "no_channels"
                else:
                    return await self.async_step_channels()

        return self.async_show_form(
            step_id="custom_url",
            data_schema=vol.Schema({vol.Required(CONF_EPG_URL): str}),
            errors=errors,
        )

    # -- Paso 2: seleccionar canales --

    async def async_step_channels(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            selected = user_input.get(CONF_CHANNELS, [])
            if not selected:
                errors["base"] = "no_channels_selected"
            else:
                # Permitir múltiples entradas por fuente (sin unique_id)
                source_name = EPG_SOURCES.get(self._source, {}).get("name", self._source)
                return self.async_create_entry(
                    title=f"What's On TV ({source_name})",
                    data={
                        CONF_EPG_SOURCE: self._source,
                        CONF_EPG_URL: self._url,
                        CONF_SCAN_INTERVAL: self._scan_interval,
                        CONF_CHANNELS: selected,
                    },
                )

        return self.async_show_form(
            step_id="channels",
            data_schema=vol.Schema({
                vol.Required(CONF_CHANNELS): SelectSelector(
                    SelectSelectorConfig(
                        options=_channel_options(self._channels),
                        multiple=True,
                        mode=SelectSelectorMode.LIST,
                    )
                ),
            }),
            description_placeholders={"total": str(len(self._channels))},
            errors=errors,
        )

    # -- Reconfigure: cambiar fuente/URL/intervalo/canales --

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Permite reconfigurar una entrada existente sin borrarla."""
        entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}

        if user_input is not None:
            source = user_input[CONF_EPG_SOURCE]
            scan = int(user_input[CONF_SCAN_INTERVAL])

            if source == "custom":
                # Guardar temporalmente y pasar al paso URL
                self._source = source
                self._scan_interval = scan
                return await self.async_step_reconfigure_custom_url()

            url = EPG_SOURCES[source].get("url_gz") or EPG_SOURCES[source]["url"]
            try:
                channels = await _fetch_channels(self.hass, url)
            except Exception:
                errors["base"] = "cannot_connect"
            else:
                if not channels:
                    errors["base"] = "no_channels"
                else:
                    self._source = source
                    self._scan_interval = scan
                    self._url = url
                    self._channels = channels
                    return await self.async_step_reconfigure_channels()

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema({
                vol.Required(CONF_EPG_SOURCE, default=entry.data.get(CONF_EPG_SOURCE, DEFAULT_SOURCE)): SelectSelector(
                    SelectSelectorConfig(options=_source_options(), mode=SelectSelectorMode.LIST)
                ),
                vol.Required(CONF_SCAN_INTERVAL, default=entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)): _interval_selector(),
            }),
            errors=errors,
        )

    async def async_step_reconfigure_custom_url(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            self._url = user_input[CONF_EPG_URL].strip()
            try:
                self._channels = await _fetch_channels(self.hass, self._url)
            except Exception:
                errors["base"] = "cannot_connect"
            else:
                if not self._channels:
                    errors["base"] = "no_channels"
                else:
                    return await self.async_step_reconfigure_channels()

        return self.async_show_form(
            step_id="reconfigure_custom_url",
            data_schema=vol.Schema({vol.Required(CONF_EPG_URL): str}),
            errors=errors,
        )

    async def async_step_reconfigure_channels(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}

        if user_input is not None:
            selected = user_input.get(CONF_CHANNELS, [])
            if not selected:
                errors["base"] = "no_channels_selected"
            else:
                return self.async_update_reload_and_abort(
                    entry,
                    data_updates={
                        CONF_EPG_SOURCE: self._source,
                        CONF_EPG_URL: self._url,
                        CONF_SCAN_INTERVAL: self._scan_interval,
                        CONF_CHANNELS: selected,
                    },
                )

        current = entry.data.get(CONF_CHANNELS, [])
        return self.async_show_form(
            step_id="reconfigure_channels",
            data_schema=vol.Schema({
                vol.Required(CONF_CHANNELS, default=current): SelectSelector(
                    SelectSelectorConfig(
                        options=_channel_options(self._channels),
                        multiple=True,
                        mode=SelectSelectorMode.LIST,
                    )
                ),
            }),
            description_placeholders={"total": str(len(self._channels))},
            errors=errors,
        )

    # -- Options flow --

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlowWithReload:
        return WhatsonTVOptionsFlow()


# ---------------------------------------------------------------------------
# Options Flow — patrón moderno HA 2026 (sin config_entry en __init__)
# OptionsFlowWithReload recarga automáticamente la integración al guardar
# ---------------------------------------------------------------------------

class WhatsonTVOptionsFlow(OptionsFlowWithReload):
    """Permite añadir/quitar canales y cambiar el intervalo sin reconfigurar."""

    def __init__(self) -> None:
        self._channels: dict[str, str] = {}

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        entry = self.config_entry  # inyectado por HA, sin pasar por __init__

        if not self._channels:
            url = entry.data.get(CONF_EPG_URL, "")
            try:
                self._channels = await _fetch_channels(self.hass, url)
            except Exception:
                errors["base"] = "cannot_connect"

        if user_input is not None and not errors:
            selected = user_input.get(CONF_CHANNELS, [])
            if not selected:
                errors["base"] = "no_channels_selected"
            else:
                scan = int(user_input.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL))
                # Actualizar entry.data con los nuevos canales e intervalo
                self.hass.config_entries.async_update_entry(
                    entry,
                    data={
                        **entry.data,
                        CONF_CHANNELS: selected,
                        CONF_SCAN_INTERVAL: scan,
                    },
                )
                # OptionsFlowWithReload recargará automáticamente la entrada
                return self.async_create_entry(title="", data={})

        current_channels = entry.data.get(CONF_CHANNELS, [])
        current_scan = entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        opts = _channel_options(self._channels) if self._channels else []

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(CONF_CHANNELS, default=current_channels): SelectSelector(
                    SelectSelectorConfig(
                        options=opts,
                        multiple=True,
                        mode=SelectSelectorMode.LIST,
                    )
                ),
                vol.Required(CONF_SCAN_INTERVAL, default=current_scan): _interval_selector(),
            }),
            description_placeholders={"total": str(len(self._channels))},
            errors=errors,
        )
