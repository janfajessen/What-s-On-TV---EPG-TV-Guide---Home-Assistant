# What's On TV — EPG TV Guide <br> Home Assistant Integration

<img src="https://github.com/janfajessen/What-s-On-TV---EPG-TV-Guide/blob/82eeef144435d0eea84c5fd1ebdc7cb73f91689b/whatson_tv_icon.png" alt="What's On TV - EPG Guide" width="300">


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
2. Add `https://github.com/janfajessen/What-s-On-TV---EPG-TV-Guide/` — category **Integration**
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



🌐 Custom URL (XMLTV .xml / .xml.gz)
---

## Requirements

- Home Assistant 2024.1+
- Python 3.12+

---
<br>
<sub> Wat is op televisie - ما هو على التلفزيون - Televiziyada nə var - Што па тэлевізары - Какво има по телевизията - Šta je na televiziji - Què hi ha a la televisió - Co je v televizi - Hvad er i fjernsynet - Was läuft im Fernsehen - Τι παίζει στην τηλεόραση - Kio estas en televido - Qué hay en la televisión - Zer dago telebistan - چه چیزی در تلویزیون است - Mitä televisiossa on - Quoi à la télévision - Que hai na televisión - מה יש בטלוויזיה - टेलीविजन पर क्या है - Što je na televiziji - Mi van a televízióban - Apa yang di televisi - Hvað er í sjónvarpinu - Cosa c'è in televisione - テレビでは何が - რა არის ტელევიზორში - Теледидарда не бар - 텔레비전에 무엇이 나오나요 - Ką per televizorių - Kas ir televīzijā - Wat is er op televisie - Hva er på fjernsynet - Qu'i a a la television - Co w telewizji - O que há na televisão - Ce este la televizor - Что по телевизору - Čo je v televízii - Kaj je na televiziji - Çfarë është në televizion - Шта је на телевизији - Vad är på tv - อะไรอยู่ในโทรทัศน์ - Televizyonda ne var - Що по телевізору - Có gì trên truyền hình - 电视上有什么 </sub>


<table border="0" cellspacing="0" cellpadding="6" width="100%">
<tr>
<td width="20%" align="left"><sub>🇪🇸 España / Espanya / Espainia</sub></td>
<td width="20%" align="left"><sub>🇦🇩 Andorra *</sub></td>
<td width="20%" align="left"><sub>🇦🇱 Shqipëria</sub></td>
<td width="20%" align="left"><sub>🇦🇷 Argentina</sub></td>
<td width="20%" align="left"><sub>🇦🇲 Հայաստան</sub></td>
</tr>
<tr>
<td width="20%" align="left"><sub>🇦🇺 Australia</sub></td>
<td width="20%" align="left"><sub>🇦🇹 Österreich</sub></td>
<td width="20%" align="left"><sub>🇦🇼 Aruba *</sub></td>
<td width="20%" align="left"><sub>🇸🇦 المملكة العربية السعودية</sub></td>
<td width="20%" align="left"><sub>🇧🇾 Беларусь</sub></td>
</tr>
<tr>
<td width="20%" align="left"><sub>🇧🇪 België / Belgique / Belgien</sub></td>
<td width="20%" align="left"><sub>🇧🇴 Bolivia</sub></td>
<td width="20%" align="left"><sub>🇧🇦 Bosna i Hercegovina / Босна и Херцеговина</sub></td>
<td width="20%" align="left"><sub>🇧🇷 Brasil</sub></td>
<td width="20%" align="left"><sub>🇧🇬 България</sub></td>
</tr>
<tr>
<td width="20%" align="left"><sub>🇨🇦 Canada</sub></td>
<td width="20%" align="left"><sub>🇨🇱 Chile</sub></td>
<td width="20%" align="left"><sub>🇨🇴 Colombia</sub></td>
<td width="20%" align="left"><sub>🇨🇷 Costa Rica</sub></td>
<td width="20%" align="left"><sub>🇭🇷 Hrvatska</sub></td>
</tr>
<tr>
<td width="20%" align="left"><sub>🇨🇿 Česká republika</sub></td>
<td width="20%" align="left"><sub>🇨🇾 Κύπρος / Kıbrıs *</sub></td>
<td width="20%" align="left"><sub>🇩🇰 Danmark</sub></td>
<td width="20%" align="left"><sub>🇩🇴 Rep. Dominicana</sub></td>
<td width="20%" align="left"><sub>🇪🇨 Ecuador</sub></td>
</tr>
<tr>
<td width="20%" align="left"><sub>🇪🇬 مصر</sub></td>
<td width="20%" align="left"><sub>🇸🇻 El Salvador</sub></td>
<td width="20%" align="left"><sub>🇫🇴 Færøerne / Føroyar *</sub></td>
<td width="20%" align="left"><sub>🇫🇮 Suomi / Finland</sub></td>
<td width="20%" align="left"><sub>🇫🇷 France</sub></td>
</tr>
<tr>
<td width="20%" align="left"><sub>🇬🇪 საქართველო</sub></td>
<td width="20%" align="left"><sub>🇩🇪 Deutschland</sub></td>
<td width="20%" align="left"><sub>🇬🇭 Ghana</sub></td>
<td width="20%" align="left"><sub>🇬🇷 Ελλάδα</sub></td>
<td width="20%" align="left"><sub>🇬🇹 Guatemala</sub></td>
</tr>
<tr>
<td width="20%" align="left"><sub>🇭🇳 Honduras</sub></td>
<td width="20%" align="left"><sub>🇭🇰 Hong Kong / 香港</sub></td>
<td width="20%" align="left"><sub>🇭🇺 Magyarország</sub></td>
<td width="20%" align="left"><sub>🇮🇪 Ireland / Éire *</sub></td>
<td width="20%" align="left"><sub>🇮🇸 Ísland</sub></td>
</tr>
<tr>
<td width="20%" align="left"><sub>🇮🇳 Bharat भारत</sub></td>
<td width="20%" align="left"><sub>🇮🇩 Indonesia</sub></td>
<td width="20%" align="left"><sub>🇮🇱 יִשְׂרָאֵל</sub></td>
<td width="20%" align="left"><sub>🇮🇹 Italia</sub></td>
<td width="20%" align="left"><sub>🇯🇵 日本</sub></td>
</tr>
<tr>
<td width="20%" align="left"><sub>🇰🇿 Қазақстан *</sub></td>
<td width="20%" align="left"><sub>🇱🇻 Latvija</sub></td>
<td width="20%" align="left"><sub>🇱🇧 لبنان</sub></td>
<td width="20%" align="left"><sub>🇱🇮 Liechtenstein *</sub></td>
<td width="20%" align="left"><sub>🇱🇹 Lietuva</sub></td>
</tr>
<tr>
<td width="20%" align="left"><sub>🇱🇺 Lëtzebuerg / Luxembourg / Luxemburg</sub></td>
<td width="20%" align="left"><sub>🇲🇰 Северна Македонија</sub></td>
<td width="20%" align="left"><sub>🇲🇾 Bahasa Melayu</sub></td>
<td width="20%" align="left"><sub>🇲🇹 Malta</sub></td>
<td width="20%" align="left"><sub>🇲🇽 México</sub></td>
</tr>
<tr>
<td width="20%" align="left"><sub>🇲🇪 Crna Gora / Црна Гора</sub></td>
<td width="20%" align="left"><sub>🇲🇦 المغرب</sub></td>
<td width="20%" align="left"><sub>🇲🇨 Monaco / Mónegue *</sub></td>
<td width="20%" align="left"><sub>🇳🇱 Nederland</sub></td>
<td width="20%" align="left"><sub>🇳🇿 New Zealand / Aotearoa</sub></td>
</tr>
<tr>
<td width="20%" align="left"><sub>🇳🇮 Nicaragua</sub></td>
<td width="20%" align="left"><sub>🇳🇬 Nigeria</sub></td>
<td width="20%" align="left"><sub>🇳🇴 Norge / Noreg</sub></td>
<td width="20%" align="left"><sub>🇵🇦 Panamá</sub></td>
<td width="20%" align="left"><sub>🇵🇾 Paraguay</sub></td>
</tr>
<tr>
<td width="20%" align="left"><sub>🇵🇪 Perú</sub></td>
<td width="20%" align="left"><sub>🇵🇭 Pilipinas</sub></td>
<td width="20%" align="left"><sub>🇵🇱 Polska</sub></td>
<td width="20%" align="left"><sub>🇵🇸 فلسطين *</sub></td>
<td width="20%" align="left"><sub>🇵🇹 Portugal</sub></td>
</tr>
<tr>
<td width="20%" align="left"><sub>🇵🇷 Puerto Rico *</sub></td>
<td width="20%" align="left"><sub>🇷🇴 România</sub></td>
<td width="20%" align="left"><sub>🇷🇺 Россия</sub></td>
<td width="20%" align="left"><sub>🇷🇸 Србија</sub></td>
<td width="20%" align="left"><sub>🇸🇲 San Marino *</sub></td>
</tr>
<tr>
<td width="20%" align="left"><sub>🇸🇬 Singapore / 新加坡 / சிங்கப்பூர் / Singapura</sub></td>
<td width="20%" align="left"><sub>🇸🇰 Slovensko</sub></td>
<td width="20%" align="left"><sub>🇸🇮 Slovenija</sub></td>
<td width="20%" align="left"><sub>🇿🇦 South Africa</sub></td>
<td width="20%" align="left"><sub>🇰🇷 대한민국</sub></td>
</tr>
<tr>
<td width="20%" align="left"><sub>🇸🇪 Sverige</sub></td>
<td width="20%" align="left"><sub>🇨🇭 Schweiz / Suisse / Svizzera / Svizra</sub></td>
<td width="20%" align="left"><sub>🇹🇼 Taiwan / 臺灣</sub></td>
<td width="20%" align="left"><sub>🇹🇭 ประเทศไทย</sub></td>
<td width="20%" align="left"><sub>🇹🇷 Türkiye</sub></td>
</tr>
<tr>
<td width="20%" align="left"><sub>🇺🇬 Uganda</sub></td>
<td width="20%" align="left"><sub>🇺🇦 Украïна</sub></td>
<td width="20%" align="left"><sub>🇦🇪 Al-Imarat</sub></td>
<td width="20%" align="left"><sub>🇬🇧 United Kingdom / Cymru</sub></td>
<td width="20%" align="left"><sub>🇺🇸 United States</sub></td>
</tr>
<tr>
<td width="20%" align="left"><sub>🇺🇾 Uruguay</sub></td>
<td width="20%" align="left"><sub>🇻🇦 Città del Vaticano *</sub></td>
<td width="20%" align="left"><sub>🇻🇪 Venezuela</sub></td>
<td width="20%" align="left"><sub>🇻🇳 Việt Nam</sub></td>
<td width="20%" align="left"><sub>🇿🇼 Zimbabwe</sub></td>
</tr>
</table>
<sub>* Channels available via regional EPG sources</sub>

---
## License

MIT — see [LICENSE](LICENSE)
