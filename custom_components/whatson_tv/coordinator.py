"""Coordinator para What's On TV EPG: descarga, parsea XMLTV y gestiona watches."""

from __future__ import annotations

import gzip
import logging
import re as _re
from datetime import datetime, timedelta, timezone
from xml.etree import ElementTree as ET

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

REQUEST_TIMEOUT      = 90
WATCHES_STORAGE_KEY  = f"{DOMAIN}_watches"
WATCHES_STORAGE_VER  = 1
NOTIFIED_STORAGE_KEY = f"{DOMAIN}_notified"
WATCHES_SHARED_KEY   = f"{DOMAIN}_watches_shared"   # clave en hass.data


class EPGCoordinator(DataUpdateCoordinator):
    """Descarga y parsea el EPG. Las watches se leen de hass.data (compartido)."""

    def __init__(self, hass: HomeAssistant, url: str, scan_interval_hours: int) -> None:
        super().__init__(
            hass, _LOGGER, name=DOMAIN,
            update_interval=timedelta(hours=scan_interval_hours),
        )
        self.url = url
        self.channels:   dict[str, dict]       = {}
        self.programmes: dict[str, list[dict]] = {}
        self._watches_store  = Store(hass, WATCHES_STORAGE_VER, WATCHES_STORAGE_KEY)
        self._notified_store = Store(hass, WATCHES_STORAGE_VER, NOTIFIED_STORAGE_KEY)
        self._notified: set[str] = set()

    # ── Acceso a watches (siempre desde hass.data) ─────────────────────────

    def _get_watches(self) -> list[dict]:
        """Lee las watches del almacén compartido en hass.data."""
        return list(self.hass.data.get(WATCHES_SHARED_KEY, []))

    def get_watches(self) -> list[dict]:
        """Interfaz pública para el sensor EPGWatchesSensor."""
        return self._get_watches()

    # ── Storage (solo el coordinator dueño escribe aquí) ───────────────────

    async def load_watches_from_storage(self) -> None:
        """Cargar watches del disco y publicar en hass.data.
        Solo debe llamarse desde el coordinator dueño al arrancar."""
        data = await self._watches_store.async_load()
        watches = data.get("watches", []) if data else []
        _LOGGER.debug("EPG WATCHES: cargadas %d watches del storage", len(watches))
        # Solo escribir si tenemos datos o si hass.data aún no tiene nada
        if watches or WATCHES_SHARED_KEY not in self.hass.data:
            self.hass.data[WATCHES_SHARED_KEY] = watches
        notified = await self._notified_store.async_load()
        self._notified = set(notified.get("keys", [])) if notified else set()

    async def _save_watches(self, watches: list[dict]) -> None:
        await self._watches_store.async_save({"watches": watches})

    async def _save_notified(self) -> None:
        now = datetime.now(tz=timezone.utc)
        self._notified = {
            k for k in self._notified
            if len(k.split("|")) >= 3 and (now - _parse_iso(k.split("|")[2])).days < 8
        }
        await self._notified_store.async_save({"keys": list(self._notified)})

    async def add_watch(self, keyword: str, notify_service: str,
                        hours_before: float, match: str = "word") -> dict:
        import uuid
        watch = {
            "id":             str(uuid.uuid4())[:8],
            "keyword":        keyword.strip(),
            "notify_service": notify_service,
            "hours_before":   float(hours_before),
            "match":          match,
        }
        watches = self._get_watches()
        watches.append(watch)
        self.hass.data[WATCHES_SHARED_KEY] = watches
        await self._save_watches(watches)
        return watch

    async def remove_watch(self, watch_id: str) -> bool:
        watches = self._get_watches()
        new_watches = [w for w in watches if w["id"] != watch_id]
        if len(new_watches) == len(watches):
            return False
        self.hass.data[WATCHES_SHARED_KEY] = new_watches
        await self._save_watches(new_watches)
        return True

    # ── Update principal (descarga EPG) ────────────────────────────────────

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

        self.channels   = result["channels"]
        self.programmes = result["programmes"]

        _LOGGER.debug("EPG actualizado: %d canales", len(self.channels))

        # Comprobar watches tras cada descarga
        watches = self._get_watches()
        if watches and self.programmes:
            await self._check_watches(watches)

        return result

    # ── Watches: comprobar y notificar ─────────────────────────────────────

    async def check_watches_now(self) -> None:
        """Llamado desde el timer global del __init__."""
        watches = self._get_watches()
        _LOGGER.warning("EPG WATCHES: tick — %d watches, %d canales en %s",
                        len(watches), len(self.programmes), self.url[:30])
        if watches and self.programmes:
            await self._check_watches(watches)

    async def _check_watches(self, watches: list[dict]) -> None:
        now = datetime.now(tz=timezone.utc)
        new_notified = False

        for watch in watches:
            keyword  = watch["keyword"].lower()
            notify   = watch["notify_service"]
            h_before = float(watch.get("hours_before", 24))
            match    = watch.get("match", "word")
            window   = timedelta(hours=h_before)

            for ch_id, progs in self.programmes.items():
                for prog in progs:
                    try:
                        start = prog["start"]
                        stop  = prog.get("stop", start)
                        if stop <= now:
                            continue

                        title_lower = prog.get("title", "").lower()

                        if match == "exact":
                            matched = (title_lower == keyword)
                        elif match == "word":
                            esc = _re.escape(keyword)
                            matched = bool(_re.search(
                                r'(?:(?<=\s)|(?<=^)|(?<=[-/(]))' + esc +
                                r'(?=\s|$|[-/.,!?)])',
                                title_lower
                            ))
                        else:
                            matched = keyword in title_lower

                        if not matched:
                            continue

                        time_to_start = start - now
                        if time_to_start.total_seconds() > window.total_seconds():
                            continue

                    except Exception as err:
                        _LOGGER.debug("_check_watches error: %s", err)
                        continue

                    key = f"{watch['id']}|{ch_id}|{start.isoformat()}"
                    if key in self._notified:
                        continue

                    ch_name = self.channels.get(ch_id, {}).get("name", ch_id)
                    secs    = max(0, int(time_to_start.total_seconds()))
                    h, m    = divmod(secs // 60, 60)
                    time_str = f"{h}h {m}min" if h else f"{m} min"
                    start_fmt = start.astimezone().strftime("%A %d/%m a las %H:%M")

                    message = (
                        f"📺 {ch_name} — {prog['title']}\n"
                        f"🕐 {start_fmt}\n"
                        f"⏰ Empieza en {time_str}"
                    )

                    try:
                        svc_name = notify.split(".", 1)[1] if "." in notify else notify
                        if self.hass.services.has_service("notify", svc_name):
                            domain, service = notify.split(".", 1)
                            await self.hass.services.async_call(
                                domain, service,
                                {"message": message, "title": f"📺 {prog['title']}"},
                                blocking=False,
                            )
                        else:
                            await self.hass.services.async_call(
                                "notify", "send_message",
                                {"message": message, "title": f"📺 {prog['title']}"},
                                target={"entity_id": notify},
                                blocking=False,
                            )
                        _LOGGER.warning("EPG WATCHES: notificación enviada → %s en %s",
                                        prog["title"], ch_name)
                    except Exception as err:
                        _LOGGER.warning("Error enviando notificación: %s", err)

                    self._notified.add(key)
                    new_notified = True

        if new_notified:
            await self._save_notified()

    # ── Parseo XMLTV ───────────────────────────────────────────────────────

    def _parse_xmltv(self, raw: bytes) -> dict:
        if raw[:2] == b"\x1f\x8b":
            raw = gzip.decompress(raw)
        root = ET.fromstring(raw.decode("utf-8", errors="replace"))

        channels: dict[str, dict]  = {}
        programmes: dict[str, list] = {}

        for ch in root.findall("channel"):
            ch_id   = ch.get("id")
            name_el = ch.find("display-name")
            icon_el = ch.find("icon")
            if ch_id and name_el is not None and name_el.text:
                channels[ch_id]   = {
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
                "start": start, "stop": stop,
                "title": title_el.text.strip(),
                "desc":  (desc_el.text or "").strip() if desc_el is not None else "",
                "icon":  icon_el.get("src") if icon_el is not None else None,
            })

        for ch_id in programmes:
            programmes[ch_id].sort(key=lambda x: x["start"])

        return {"channels": channels, "programmes": programmes}

    # ── Helpers ────────────────────────────────────────────────────────────

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
        s       = time_str.strip()
        dt_part = s[:14]
        tz_part = s[14:].strip() if len(s) > 14 else "+0000"
        dt      = datetime.strptime(dt_part, "%Y%m%d%H%M%S")
        sign    = 1 if tz_part.startswith("+") else -1
        tz_part = tz_part.lstrip("+-")
        tz_h    = int(tz_part[:2]) if len(tz_part) >= 2 else 0
        tz_m    = int(tz_part[2:4]) if len(tz_part) >= 4 else 0
        offset  = timedelta(hours=tz_h, minutes=tz_m) * sign
        return (dt - offset).replace(tzinfo=timezone.utc)
    except (ValueError, IndexError):
        return None


def _parse_iso(s: str) -> datetime:
    try:
        dt = datetime.fromisoformat(s)
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except ValueError:
        return datetime.now(tz=timezone.utc)
        