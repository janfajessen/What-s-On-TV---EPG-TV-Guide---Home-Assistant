# What's On TV — Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![HA Version](https://img.shields.io/badge/Home%20Assistant-2024.1%2B-blue)](https://www.home-assistant.io/)

A worldwide EPG (Electronic Programme Guide) integration for Home Assistant. Turns any XMLTV-compatible TV guide source into HA sensors — one sensor per channel, updated automatically.

> **Highly recommended companions:**
> - 📺 [What's On TV — EPG Card](https://github.com/YOUR_GITHUB_USER/whatsontv-epg-card) — visual TV guide card for Lovelace
> - 🔔 [What's On TV — Notify Card](https://github.com/YOUR_GITHUB_USER/whatsontv-notify-card) — search programmes and set keyword alerts

---

## Features

- **82 countries** supported.
- One **sensor per channel** with current programme, next programme, progress percentage and full schedule
- **Keyword watches** — save a keyword and get notified when a matching programme appears in the guide, via any HA notification service
- Watches stored in **HA Storage** (persistent across restarts and devices)
- Supports **multiple instances** (different EPG sources simultaneously)
- Automatic refresh (configurable interval, 1–24 h)

---

## Installation

### Via HACS (recommended)

1. Open HACS → **Integrations** → ⋮ → **Custom repositories**
2. Add `https://github.com/YOUR_GITHUB_USER/whatson_tv` — category **Integration**
3. Search for **What's On TV** and install
4. Restart Home Assistant

### Manual

Copy the `custom_components/whatson_tv/` folder to your HA `config/custom_components/` directory and restart.

---

## Configuration

Go to **Settings → Devices & Services → Add Integration → What's On TV**.

**Step 1 — Source:** select your country/EPG source and update interval.

**Step 2 — Channels:** select the channels you want to track (the list is fetched live from the EPG source).

You can add multiple entries for different countries simultaneously.

---

## Sensor Attributes

Each channel sensor (`sensor.epg_<channel_name>`) exposes:

| Attribute | Description |
|---|---|
| `title` | Current programme title |
| `start` / `end` | Start / end time (ISO 8601 UTC) |
| `description` | Programme description |
| `image` | Programme artwork URL |
| `progress_pct` | Current programme progress (0–100) |
| `next_title` | Next programme title |
| `next_start` / `next_end` | Next programme times |
| `channel_id` | Channel ID in the EPG source |
| `channel_name` | Channel display name |
| `channel_icon` | Channel logo URL |
| `schedule` | List of upcoming programmes (up to 50) |

---

## Services

### `whatson_tv.add_watch`

```yaml
action: whatson_tv.add_watch
data:
  keyword: "Champions"
  notify_service: "notify.telegram_mybot"
  hours_before: 2   # optional, default 24
```

### `whatson_tv.remove_watch`

```yaml
action: whatson_tv.remove_watch
data:
  watch_id: "abc12345"
```

---

## Automations — Future Programme Notifications

You can replicate the Notify Card watch behaviour directly in HA automations:

```yaml
alias: "EPG — Notify when Champions League appears"
trigger:
  - platform: template
    value_template: >
      {% set keyword = "champions" %}
      {% set hours_before = 2 %}
      {% for state in states.sensor %}
        {% if state.attributes.channel_id is defined %}
          {% for prog in state.attributes.programacion | default([]) %}
            {% set start = prog.inicio | as_datetime %}
            {% set diff_h = ((start - now()).total_seconds() / 3600) %}
            {% if keyword in prog.titulo | lower and diff_h >= 0 and diff_h <= hours_before %}
              true
            {% endif %}
          {% endfor %}
        {% endif %}
      {% endfor %}
condition: []
action:
  - action: notify.telegram_mybot
    data:
      message: >
        {% for state in states.sensor %}
          {% if state.attributes.channel_id is defined %}
            {% for prog in state.attributes.programacion | default([]) %}
              {% set start = prog.inicio | as_datetime %}
              {% set diff_h = ((start - now()).total_seconds() / 3600) %}
              {% if "champions" in prog.titulo | lower and diff_h >= 0 and diff_h <= 2 %}
                📺 {{ state.attributes.channel_name }} — {{ prog.titulo }}
                🕐 {{ start | as_local | as_timestamp | timestamp_custom('%H:%M') }}
              {% endif %}
            {% endfor %}
          {% endif %}
        {% endfor %}
```

> **Tip:** Use the **Notify Card** for a simpler no-code experience — it handles watches automatically without writing automations.

---

## EPG Sources

| Key | Source | Notes |
|---|---|---|
| `epg_doblem` | EPG dobleM | Spain, updated 4×/day |
| `tdtchannels` | TDTChannels | Spain |
| `freeview_uk` | Freeview EPG | United Kingdom |
| `es`, `mx`, `de`, `fr`, `it`, `pt` … | iptv-epg.org | 82 countries |

| `custom` | Custom URL | Any XMLTV `.xml` or `.xml.gz` |


🇪🇸 España, 🇦🇩 Andorra, 🇦🇱 Shqipëria, 🇦🇷 Argentina, 🇦🇲 Հայաստան, 🇦🇺 Australia, 🇦🇹 Österreich, 🇧🇾 Беларусь, 🇧🇪 België / Belgique, 🇧🇴 Bolivia, 🇧🇦 Bosna i Hercegovina, 🇧🇷 Brasil, 🇧🇬 България, 🇨🇦 Canada, 🇨🇱 Chile, 🇨🇴 Colombia, 🇨🇷 Costa Rica, 🇭🇷 Hrvatska, 🇨🇿 Česká republika, 🇩🇰 Danmark, 🇩🇴 República Dominicana, 🇪🇨 Ecuador, 🇪🇬 مصر, 🇸🇻 El Salvador, 🇫🇮 Suomi, 🇫🇷 France, 🇬🇪 საქართველო, 🇩🇪 Deutschland, 🇬🇭 Ghana, 🇬🇷 Ελλάδα,🇬🇹 Guatemala, 🇭🇳 Honduras, 🇭🇰 Hong Kong 香港, 🇭🇺 Magyarország, 🇮🇸 Ísland, 🇮🇳 Bharat भारत, 🇮🇩 Bahasa Indonesia, 🇮🇱 יִשְׂרָאֵל,🇮🇹 Italia, 🇯🇵 日本, 🇱🇻 Latvija, 🇱🇧 لبنان,🇱🇹 Lietuva, 🇱🇺 Lëtzebuerg, 🇲🇰 Северна Македонија, 🇲🇾 Bahasa Melayu, 🇲🇹 Malta, 🇲🇽 México, 🇲🇪 Crna Gora, 🇲🇦 المغرب, 🇳🇱 Nederland, 🇳🇿 New Zealand, 🇳🇮 Nicaragua, 🇳🇬 Nigeria, 🇳🇴 Norge, 🇵🇦 Panamá, 🇵🇾 Paraguay, 🇵🇪 Perú, 🇵🇭 Pilipinas, 🇵🇱 Polska, 🇵🇹 Portugal, 🇵🇷 Puerto Rico, 🇷🇴 România, 🇷🇺 Россия, 🇷🇸 Српски, 🇸🇬 Singapore, 🇸🇰 Slovensko, 🇸🇮 Slovenija, 🇿🇦 South Africa, 🇰🇷 대한민국, 🇸🇪 Sverige, 🇨🇭 Schweiz / Suisse / Svizzera, 🇹🇼 Taiwan, 🇹🇭 Prathet Thai, 🇹🇷 Türkiye, 🇺🇦 Ukrayina, 🇦🇪 Al-Imarat, 🇬🇧 United Kingdom, 🇺🇸 United States, 🇺🇾 Uruguay, 🇻🇪 Venezuela, 🇻🇳 Việt Nam

🌐 Custom URL (XMLTV .xml / .xml.gz)
---

## Requirements

- Home Assistant 2024.1+
- Python 3.12+

---

## License

MIT — see [LICENSE](LICENSE)
