"""Coordinator para What's On TV EPG: descarga, parsea XMLTV y gestiona watches."""

from __future__ import annotations

import gzip
import logging
from datetime import datetime, timedelta, timezone
from xml.etree import ElementTree as ET

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

REQUEST_TIMEOUT = 90
WATCHES_STORAGE_KEY = f"{DOMAIN}_watches"
WATCHES_STORAGE_VERSION = 1
NOTIFIED_STORAGE_KEY = f"{DOMAIN}_notified"


class EPGCoordinator(DataUpdateCoordinator):
    """Descarga y parsea el EPG en formato XMLTV. Gestiona watches/alertas."""

    def __init__(self, hass: HomeAssistant, url: str, scan_interval_hours: int) -> None:
        super().__init__(
            hass, _LOGGER, name=DOMAIN,
            update_interval=timedelta(hours=scan_interval_hours),
        )
        self.url = url
        self.channels: dict[str, dict] = {}
        self.programmes: dict[str, list[dict]] = {}
        self._watches_store  = Store(hass, WATCHES_STORAGE_VERSION, WATCHES_STORAGE_KEY)
        self._notified_store = Store(hass, WATCHES_STORAGE_VERSION, NOTIFIED_STORAGE_KEY)
        self._watches: list[dict]  = []   # [{id, keyword, notify_service, hours_before}]
        self._notified: set[str]   = set() # claves "watch_id|channel_id|start_iso"

    # ── Storage de watches ──────────────────────────────────────────────────

    async def async_load_watches(self) -> None:
        data = await self._watches_store.async_load()
        self._watches = data.get("watches", []) if data else []
        notified = await self._notified_store.async_load()
        self._notified = set(notified.get("keys", [])) if notified else set()

    async def _save_watches(self) -> None:
        await self._watches_store.async_save({"watches": self._watches})

    async def _save_notified(self) -> None:
        # Limpiar claves antiguas (más de 7 días) para no crecer indefinidamente
        now = datetime.now(tz=timezone.utc)
        clean = set()
        for key in self._notified:
            parts = key.split("|")
            if len(parts) >= 3:
                try:
                    dt = datetime.fromisoformat(parts[2])
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    if (now - dt).days < 8:
                        clean.add(key)
                except ValueError:
                    pass
        self._notified = clean
        await self._notified_store.async_save({"keys": list(self._notified)})

    def get_watches(self) -> list[dict]:
        return list(self._watches)

    async def add_watch(self, keyword: str, notify_service: str, hours_before: int) -> dict:
        import uuid
        watch = {
            "id":             str(uuid.uuid4())[:8],
            "keyword":        keyword.strip(),
            "notify_service": notify_service,
            "hours_before":   int(hours_before),
        }
        self._watches.append(watch)
        await self._save_watches()
        return watch

    async def remove_watch(self, watch_id: str) -> bool:
        before = len(self._watches)
        self._watches = [w for w in self._watches if w["id"] != watch_id]
        if len(self._watches) < before:
            await self._save_watches()
            return True
        return False

    # ── Update principal ────────────────────────────────────────────────────

    async def _async_update_data(self) -> dict:
        session = async_get_clientsession(self.hass)
        try:
            import aiohttp
            async with session.get(
                self.url, timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
            ) as resp:
                resp.raise_for_status()
                raw = await resp.read()
        except Exception as err:
            raise UpdateFailed(f"Error descargando EPG: {err}") from err

        try:
            result = await self.hass.async_add_executor_job(self._parse_xmltv, raw)
        except Exception as err:
            raise UpdateFailed(f"Error parseando EPG: {err}") from err

        self.channels  = result["channels"]
        self.programmes = result["programmes"]

        _LOGGER.debug(
            "EPG actualizado: %d canales, %d con programación",
            len(self.channels),
            sum(1 for p in self.programmes.values() if p),
        )

        # Comprobar watches tras cada actualización
        if self._watches:
            await self._check_watches()

        return result

    # ── Watches: comprobar y notificar ──────────────────────────────────────

    async def _check_watches(self) -> None:
        now = datetime.now(tz=timezone.utc)
        new_notified = False

        for watch in self._watches:
            keyword  = watch["keyword"].lower()
            notify   = watch["notify_service"]
            h_before = watch.get("hours_before", 24)
            window   = timedelta(hours=h_before)

            for ch_id, progs in self.programmes.items():
                for prog in progs:
                    start = prog["start"]
                    if start <= now:
                        continue  # ya empezó

                    title_lower = prog["title"].lower()
                    if keyword not in title_lower:
                        continue

                    # Solo notificar si faltan menos de h_before horas
                    time_to_start = start - now
                    if time_to_start > window:
                        continue

                    key = f"{watch['id']}|{ch_id}|{start.isoformat()}"
                    if key in self._notified:
                        continue  # ya notificado

                    # Mandar notificación
                    ch_name = self.channels.get(ch_id, {}).get("name", ch_id)
                    hours_left = int(time_to_start.total_seconds() // 3600)
                    mins_left  = int((time_to_start.total_seconds() % 3600) // 60)
                    time_str   = f"{hours_left}h {mins_left}min" if hours_left else f"{mins_left} min"

                    start_local = start.astimezone()
                    start_fmt   = start_local.strftime("%A %d/%m a las %H:%M")

                    message = (
                        f"📺 {ch_name} — {prog['title']}\n"
                        f"🕐 {start_fmt}\n"
                        f"⏰ Empieza en {time_str}"
                    )

                    try:
                        domain, service = notify.split(".", 1)
                        await self.hass.services.async_call(
                            domain, service,
                            {"message": message, "title": f"📺 {prog['title']}"},
                            blocking=False,
                        )
                        _LOGGER.info("Watch '%s' → notificación enviada: %s en %s", keyword, prog["title"], ch_name)
                    except Exception as err:
                        _LOGGER.warning("Error enviando notificación watch '%s': %s", keyword, err)

                    self._notified.add(key)
                    new_notified = True

        if new_notified:
            await self._save_notified()

    # ── Parseo XMLTV ────────────────────────────────────────────────────────

    def _parse_xmltv(self, raw: bytes) -> dict:
        if raw[:2] == b"\x1f\x8b":
            raw = gzip.decompress(raw)
        content = raw.decode("utf-8", errors="replace")
        root    = ET.fromstring(content)

        channels:  dict[str, dict]   = {}
        programmes: dict[str, list]  = {}

        for ch in root.findall("channel"):
            ch_id   = ch.get("id")
            name_el = ch.find("display-name")
            icon_el = ch.find("icon")
            if ch_id and name_el is not None and name_el.text:
                channels[ch_id] = {
                    "name": name_el.text.strip(),
                    "icon": icon_el.get("src") if icon_el is not None else None,
                }
                programmes[ch_id] = []

        for prog in root.findall("programme"):
            ch_id = prog.get("channel")
            if ch_id not in programmes:
                continue
            start = _parse_xmltv_dt(prog.get("start"))
            stop  = _parse_xmltv_dt(prog.get("stop"))
            if not start or not stop:
                continue
            title_el = prog.find("title")
            desc_el  = prog.find("desc")
            icon_el  = prog.find("icon")
            if title_el is None or not title_el.text:
                continue
            programmes[ch_id].append({
                "start": start,
                "stop":  stop,
                "title": title_el.text.strip(),
                "desc":  (desc_el.text or "").strip() if desc_el is not None else "",
                "icon":  icon_el.get("src") if icon_el is not None else None,
            })

        for ch_id in programmes:
            programmes[ch_id].sort(key=lambda x: x["start"])

        return {"channels": channels, "programmes": programmes}

    # ── Helpers para sensores ───────────────────────────────────────────────

    def get_current_and_next(self, channel_id: str) -> tuple[dict | None, dict | None]:
        now   = datetime.now(tz=timezone.utc)
        progs = self.programmes.get(channel_id, [])
        current = next_prog = None
        for i, prog in enumerate(progs):
            if prog["start"] <= now < prog["stop"]:
                current = prog
                if i + 1 < len(progs):
                    next_prog = progs[i + 1]
                break
            elif prog["start"] > now and next_prog is None:
                next_prog = prog
        return current, next_prog

    def get_sorted_channel_list(self) -> list[tuple[str, str]]:
        return sorted(
            ((ch_id, info["name"]) for ch_id, info in self.channels.items()),
            key=lambda x: x[1].lower(),
        )


def _parse_xmltv_dt(time_str: str | None) -> datetime | None:
    if not time_str:
        return None
    try:
        time_str = time_str.strip()
        dt_part  = time_str[:14]
        tz_part  = time_str[14:].strip() if len(time_str) > 14 else "+0000"
        dt       = datetime.strptime(dt_part, "%Y%m%d%H%M%S")
        sign     = 1 if tz_part.startswith("+") else -1
        tz_part  = tz_part.lstrip("+-")
        tz_h     = int(tz_part[:2]) if len(tz_part) >= 2 else 0
        tz_m     = int(tz_part[2:4]) if len(tz_part) >= 4 else 0
        offset   = timedelta(hours=tz_h, minutes=tz_m) * sign
        return (dt - offset).replace(tzinfo=timezone.utc)
    except (ValueError, IndexError):
        return None
