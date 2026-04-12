"""Sensores EPG para What's On TV."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_CHANNELS, DOMAIN
from .coordinator import EPGCoordinator

_LOGGER = logging.getLogger(__name__)
MAX_SCHEDULE = 50  # máximo de programas futuros en el atributo programacion


async def async_setup_entry(
    hass: HomeAssistant,
    entry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: EPGCoordinator = entry.runtime_data.coordinator
    selected: list[str] = entry.data.get(CONF_CHANNELS, [])
    valid = [ch for ch in selected if ch in coordinator.channels]

    if not valid:
        _LOGGER.warning(
            "Ningún canal seleccionado coincide con el EPG. "
            "Seleccionados: %s | En EPG: %d canales",
            selected[:5], len(coordinator.channels),
        )
        valid = list(coordinator.channels.keys())

    entities: list[SensorEntity] = [
        EPGChannelSensor(coordinator, ch_id, entry) for ch_id in valid
    ]
    entities.append(EPGWatchesSensor(coordinator, entry))
    async_add_entities(entities)


def _device_info(entry) -> DeviceInfo:
    return DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name=entry.title,
        manufacturer="What's On TV",
        model="EPG Integration",
        entry_type="service",
    )


class EPGChannelSensor(CoordinatorEntity, SensorEntity):
    """Un sensor por canal — expone programa actual, siguiente y programación."""

    def __init__(self, coordinator: EPGCoordinator, channel_id: str, entry) -> None:
        super().__init__(coordinator)
        self._channel_id = channel_id
        ch = coordinator.channels.get(channel_id, {})
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_{channel_id}"
        self._attr_name = f"EPG {ch.get('name', channel_id)}"
        self._attr_device_info = _device_info(entry)
        self._attr_icon = "mdi:television-play"
        self._unsub_timer = None

    # ── Estado ──────────────────────────────────────────────────────────────

    @property
    def state(self) -> str:
        current, _ = self.coordinator.get_current_and_next(self._channel_id)
        return current["title"] if current else "Sin datos"

    @property
    def extra_state_attributes(self) -> dict:
        ch = self.coordinator.channels.get(self._channel_id, {})
        current, nxt = self.coordinator.get_current_and_next(self._channel_id)
        now = datetime.now(tz=timezone.utc)

        # Progreso del programa actual (0–100)
        progreso = 0
        if current:
            total = (current["stop"] - current["start"]).total_seconds()
            elapsed = (now - current["start"]).total_seconds()
            progreso = round(min(100, max(0, elapsed / total * 100)) if total > 0 else 0, 1)

        def fmt(dt: datetime | None) -> str | None:
            return dt.isoformat() if dt else None

        # Lista de programación no terminada (hasta MAX_SCHEDULE entradas)
        progs_raw = self.coordinator.programmes.get(self._channel_id, [])
        programacion = []
        for p in progs_raw:
            if p["stop"] < now and (current is None or p["start"] != current["start"]):
                continue  # saltar programas ya terminados excepto el actual
            en_curso = current is not None and p["start"] == current["start"]
            if len(programacion) >= MAX_SCHEDULE:
                break
            programacion.append({
                "title":      p["title"],
                "start":      fmt(p["start"]),
                "end":         fmt(p["stop"]),
                "description": p.get("desc", ""),
                "image":      p.get("icon"),
                "on_air":    en_curso,
            })

        return {
            # Programa actual
            "title":      current["title"] if current else None,
            "start":      fmt(current["start"]) if current else None,
            "end":         fmt(current["stop"]) if current else None,
            "description": current.get("desc", "") if current else None,
            "image":      current.get("icon") if current else None,
            "progress_pct": progreso,
            # Siguiente programa
            "next_title":      nxt["title"] if nxt else None,
            "next_start":      fmt(nxt["start"]) if nxt else None,
            "next_end":         fmt(nxt["stop"]) if nxt else None,
            "next_description": nxt.get("desc", "") if nxt else None,
            # Info canal
            "channel_id":   self._channel_id,
            "channel_name": ch.get("name", self._channel_id),
            "channel_icon": ch.get("icon"),
            # Programación completa
            "schedule": programacion,
        }

    # ── Timer de refresco ────────────────────────────────────────────────────

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()

        @callback
        def _tick(_now: datetime) -> None:
            """Refresco cada 5 min en el event loop. @callback = thread-safe."""
            self.async_write_ha_state()

        self._unsub_timer = async_track_time_interval(
            self.hass, _tick, timedelta(minutes=5)
        )

    async def async_will_remove_from_hass(self) -> None:
        if self._unsub_timer:
            self._unsub_timer()
            self._unsub_timer = None


class EPGWatchesSensor(CoordinatorEntity, SensorEntity):
    """Sensor que expone las watches guardadas (para lectura desde JS card)."""

    def __init__(self, coordinator: EPGCoordinator, entry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_watches"
        self._attr_name = "EPG Watches"
        self._attr_device_info = _device_info(entry)
        self._attr_icon = "mdi:bell-ring"

    @property
    def state(self) -> int:
        return len(self.coordinator.get_watches())

    @property
    def extra_state_attributes(self) -> dict:
        return {"watches": self.coordinator.get_watches()}
        