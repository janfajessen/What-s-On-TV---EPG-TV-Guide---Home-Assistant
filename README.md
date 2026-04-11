# What's On TV — EPG TV Guide <br> Home Assistant Integration

<img src="https://raw.githubusercontent.com/janfajessen/What-s-On-TV---EPG-TV-Guide/24d6adf4347ca21757a2514c559a572179c582e5/Whats_On_TV.png" alt="What's On TV - EPG Guide" width="100">


[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2026.2%2B-41bdf5.svg?style=for-the-badge)](https://www.home-assistant.io/)
[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41bdf5.svg?style=for-the-badge)](https://hacs.xyz/docs/publish/start)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Donate-yellow.svg?style=for-the-badge)](https://www.buymeacoffee.com/janfajessen)
[![Patreon](https://img.shields.io/badge/Patreon-Support-red.svg?style=for-the-badge)](https://www.patreon.com/janfajessen)

<sub> Wat is op televisie - ما هو على التلفزيون - Televiziyada nə var - Што па тэлевізары - Какво има по телевизията - Šta je na televiziji - Què hi ha a la televisió - Co je v televizi - Hvad er i fjernsynet - Was läuft im Fernsehen - Τι παίζει στην τηλεόραση - Kio estas en televido - Qué hay en la televisión - Zer dago telebistan - چه چیزی در تلویزیون است - Mitä televisiossa on - Quoi à la télévision - Que hai na televisión - מה יש בטלוויזיה - टेलीविजन पर क्या है - Što je na televiziji - Mi van a televízióban - Apa yang di televisi - Hvað er í sjónvarpinu - Cosa c'è in televisione - テレビでは何が - რა არის ტელევიზორში - Теледидарда не бар - 텔레비전에 무엇이 나오나요 - Ką per televizorių - Kas ir televīzijā - Wat is er op televisie - Hva er på fjernsynet - Qu'i a a la television - Co w telewizji - O que há na televisão - Ce este la televizor - Что по телевизору - Čo je v televízii - Kaj je na televiziji - Çfarë është në televizion - Шта је на телевизији - Vad är på tv - อะไรอยู่ในโทรทัศน์ - Televizyonda ne var - Що по телевізору - Có gì trên truyền hình - 电视上有什么 </sub>


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
<sub> Wat is op televisie - ما هو على التلفزيون - Televiziyada nə var - Што па тэлевізары - Какво има по телевизията - Šta je na televiziji - Què hi ha a la televisió - Co je v televizi - Hvad er i fjernsynet - Was läuft im Fernsehen - Τι παίζει στην τηλεόραση - Kio estas en televido - Qué hay en la televisión - Zer dago telebistan - چه چیزی در تلویزیون است - Mitä televisiossa on - Quoi à la télévision - Que hai na televisión - מה יש בטלוויזיה - टेलीविजन पर क्या है - Što je na televiziji - Mi van a televízióban - Apa yang di televisi - Hvað er í sjónvarpinu - Cosa c'è in televisione - テレビでは何が - რა არის ტელევიზორში - Теледидарда не бар - 텔레비전에 무엇이 나오나요 - Ką per televizorių - Kas ir televīzijā - Wat is er op televisie - Hva er på fjernsynet - Qu'i a a la television - Co w telewizji - O que há na televisão - Ce este la televizor - Что по телевизору - Čo je v televízii - Kaj je na televiziji - Çfarë është në televizion - Шта је на телевизији - Vad är på tv - อะไรอยู่ในโทรทัศน์ - Televizyonda ne var - Що по телевізору - Có gì trên truyền hình - 电视上有什么 </sub>
<sub>
<sub>

<table border="0" cellspacing="0" cellpadding="4">
<tr>
<td>🇪🇸 España</td><td>🇦🇩 Andorra</td><td>🇦🇱 Shqipëria</td><td>🇦🇷 Argentina</td><td>🇦🇲 Հայաստան</td><td>🇦🇺 Australia</td><td>🇦🇹 Österreich</td>
</tr><tr>
<td>🇧🇾 Беларусь</td><td>🇧🇪 België/Belgique</td><td>🇧🇴 Bolivia</td><td>🇧🇦 Bosna i Hercegovina</td><td>🇧🇷 Brasil</td><td>🇧🇬 България</td><td>🇨🇦 Canada</td>
</tr><tr>
<td>🇨🇱 Chile</td><td>🇨🇴 Colombia</td><td>🇨🇷 Costa Rica</td><td>🇭🇷 Hrvatska</td><td>🇨🇿 Česká republika</td><td>🇩🇰 Danmark</td><td>🇩🇴 Rep. Dominicana</td>
</tr><tr>
<td>🇪🇨 Ecuador</td><td>🇪🇬 مصر</td><td>🇸🇻 El Salvador</td><td>🇫🇮 Suomi</td><td>🇫🇷 France</td><td>🇬🇪 საქართველო</td><td>🇩🇪 Deutschland</td>
</tr><tr>
<td>🇬🇭 Ghana</td><td>🇬🇷 Ελλάδα</td><td>🇬🇹 Guatemala</td><td>🇭🇳 Honduras</td><td>🇭🇰 Hong Kong 香港</td><td>🇭🇺 Magyarország</td><td>🇮🇸 Ísland</td>
</tr><tr>
<td>🇮🇳 Bharat भारत</td><td>🇮🇩 Indonesia</td><td>🇮🇱 יִשְׂרָאֵל</td><td>🇮🇹 Italia</td><td>🇯🇵 日本</td><td>🇱🇻 Latvija</td><td>🇱🇧 لبنان</td>
</tr><tr>
<td>🇱🇹 Lietuva</td><td>🇱🇺 Lëtzebuerg</td><td>🇲🇰 Северна Македонија</td><td>🇲🇾 Bahasa Melayu</td><td>🇲🇹 Malta</td><td>🇲🇽 México</td><td>🇲🇪 Crna Gora</td>
</tr><tr>
<td>🇲🇦 المغرب</td><td>🇳🇱 Nederland</td><td>🇳🇿 New Zealand</td><td>🇳🇮 Nicaragua</td><td>🇳🇬 Nigeria</td><td>🇳🇴 Norge</td><td>🇵🇦 Panamá</td>
</tr><tr>
<td>🇵🇾 Paraguay</td><td>🇵🇪 Perú</td><td>🇵🇭 Pilipinas</td><td>🇵🇱 Polska</td><td>🇵🇹 Portugal</td><td>🇵🇷 Puerto Rico</td><td>🇷🇴 România</td>
</tr><tr>
<td>🇷🇺 Россия</td><td>🇷🇸 Српски</td><td>🇸🇬 Singapore</td><td>🇸🇰 Slovensko</td><td>🇸🇮 Slovenija</td><td>🇿🇦 South Africa</td><td>🇰🇷 대한민국</td>
</tr><tr>
<td>🇸🇪 Sverige</td><td>🇨🇭 Schweiz/Suisse/Svizzera</td><td>🇹🇼 Taiwan</td><td>🇹🇭 ประเทศไทย</td><td>🇹🇷 Türkiye</td><td>🇺🇦 Ukrayina</td><td>🇦🇪 Al-Imarat</td>
</tr><tr>
<td>🇬🇧 United Kingdom</td><td>🇺🇸 United States</td><td>🇺🇾 Uruguay</td><td>🇻🇪 Venezuela</td><td>🇻🇳 Việt Nam</td><td></td><td></td>
</tr>
</table>

</sub>

🌐 Custom URL (XMLTV .xml / .xml.gz)
---

## Requirements

- Home Assistant 2024.1+
- Python 3.12+

---

## License

MIT — see [LICENSE](LICENSE)
