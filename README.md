<div align="center">

# What's On TV 
## EPG TV Guide <br> Home Assistant Integration
..........   <img src="custom_components/whatson_tv/brand/logo@2x.png" width="550"/>

![Version](https://img.shields.io/badge/version-1.5.24-blue?style=for-the-badge)
![HA](https://img.shields.io/badge/Home%20Assistant-2024.1+-orange?style=for-the-badge&logo=home-assistant)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python)
![HACS](https://img.shields.io/badge/HACS-Custom-41BDF5?style=for-the-badge&logo=homeassistantcommunitystore&logoColor=white)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Donate-yellow?style=for-the-badge&logo=buymeacoffee)](https://www.buymeacoffee.com/janfajessen)
[![Patreon](https://img.shields.io/badge/Patreon-Support-red?style=for-the-badge&logo=patreon)](https://www.patreon.com/janfajessen)
<!--[![Ko-Fi](https://img.shields.io/badge/Ko--Fi-Support-teal?style=for-the-badge&logo=ko-fi)](https://ko-fi.com/janfajessen)
[![GitHub Sponsors](https://img.shields.io/badge/GitHub%20Sponsors-Support-pink?style=for-the-badge&logo=githubsponsors)](https://github.com/sponsors/janfajessen)


[![PayPal](https://img.shields.io/badge/PayPal-Donate-blue?style=for-the-badge&logo=paypal)](https://paypal.me/janfajessen)-->


<sub> Wat is op televisie - ما هو على التلفزيون - Televiziyada nə var - Што па тэлевізары - Какво има по телевизията - Šta je na televiziji - Què hi ha a la televisió - Co je v televizi - Hvad er i fjernsynet - Was läuft im Fernsehen - Τι παίζει στην τηλεόραση - Kio estas en televido - Qué hay en la televisión - Zer dago telebistan - چه چیزی در تلویزیون است - Mitä televisiossa on - Quoi à la télévision - Que hai na televisión - מה יש בטלוויזיה - टेलीविजन पर क्या है - Što je na televiziji - Mi van a televízióban - Apa yang di televisi - Hvað er í sjónvarpinu - Cosa c'è in televisione - テレビでは何が - რა არის ტელევიზორში - Теледидарда не бар - 텔레비전에 무엇이 나오나요 - Ką per televizorių - Kas ir televīzijā - Wat is er op televisie - Hva er på fjernsynet - Qu'i a a la television - Co w telewizji - O que há na televisão - Ce este la televizor - Что по телевизору - Čo je v televízii - Kaj je na televiziji - Çfarë është në televizion - Шта је на телевизији - Vad är på tv - อะไรอยู่ในโทรทัศน์ - Televizyonda ne var - Що по телевізору - Có gì trên truyền hình - 电视上有什么 </sub>

</div>

## 🔍 Never miss what you want to watch

The keyword watch system lets you search across all configured EPG sources simultaneously. Some ideas:

- ⚽ **Missed the live match and want to catch the replay?** Set a watch for `"LaLiga"`, `"Champions"`, `"Libertadores"`, or `"Premier League"` — you'll get notified before the replay airs, without any spoilers in the notification
- 🎬 **Looking for a classic you can never find?** Try `"Funny games"`, `"The Apartment"`, `Rope`, `"Casablanca"`, `"Blade Runner"`, `"The Godfather"` or `"2001"` — old films rotate on cable channels more often than you'd think
- 📺 **Never miss your favourite show:** Set `"Alone"`, `"MasterChef"`, `"Survivor"` or `"Who Wants to Be a Millionaire"` and get alerted before it starts
- 🎤 **Music fan?** Search `"Eminem"`,`"Glastonbury"`, `"Eurovision"` or your favourite artist's name
- 🌍 **Documentary hunter?** Try `"Planet Earth"`, `"Cosmos"` or `"Ken Burns"` — they rerun constantly on documentary channels
- 🏎️ **Sports in general:** `"ATP1000"`,`"Formula 1"`, `"La vuelta"`, `"NBA"` — works across all your configured countries simultaneously
- 🦈 The ultimate channel surfing trap: Set `"Jaws"` — it's been airing every summer weekend since 1975 and somehow always catches you off guard
- 🎄 Tired of missing the annual TV tradition? Set a watch for `"Home Alone"` — because it airs every Christmas on at least 12 channels simultaneously, and somehow you always miss it.

> The **Word** match mode finds `"Friends"` but not `"Girlfriends"` or `"Unfriendly"`. The **Contains** mode is broader. Use **Exact** only for very specific titles.

A worldwide EPG (Electronic Programme Guide) integration for Home Assistant. Turns any XMLTV-compatible TV guide source into HA sensors — one sensor per channel, updated automatically.

> **Highly recommended companions:**
> - 📺 [What's On TV — EPG Card](https://github.com/janfajessen/What-s-On-TV-EPG-TV-Guide-Card) — visual TV guide card for Lovelace
> - 🔔 [What's On TV — Notify Card](https://github.com/janfajessen/What-s-On-TV-Search-and-Notify-Card/) — search programmes and set keyword alerts

---

## Features

- **115 countries** supported.
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


> **Highly recommended companions:**
> - 📺 [What's On TV — EPG Card](https://github.com/janfajessen/What-s-On-TV-EPG-TV-Guide-Card) — visual TV guide card for Lovelace

<div align="center">
  
<img src="https://github.com/janfajessen/What-s-On-TV---EPG-TV-Guide/blob/d4deaf321838ca168cf93711ef0f6c7fbcde8ea3/whatsontv_epg_card_configuration.png" alt="What's On TV - EPG Card configuration" width="120">  <img src="https://github.com/janfajessen/What-s-On-TV---EPG-TV-Guide/blob/9ba9d7b60cbfdd7163d9335770745f593c9c0002/whatsontv_epg_card_light_card.png" alt="What's On TV - EPG light Card" width="120"> <img src="https://github.com/janfajessen/What-s-On-TV---EPG-TV-Guide/blob/c182f8324b4c54bc2a82bcd817de789b43c2208d/whatsontv_epg_card.png" alt="What's On TV - EPG Card" width="120">  <img src="https://github.com/janfajessen/What-s-On-TV---EPG-TV-Guide/blob/c182f8324b4c54bc2a82bcd817de789b43c2208d/whatsontv_epg_card_programme.png" alt="What's On TV - EPG Card programme" width="120">  <img src="https://github.com/janfajessen/What-s-On-TV---EPG-TV-Guide/blob/c182f8324b4c54bc2a82bcd817de789b43c2208d/whatsontv_epg_card_programacion.png" alt="What's On TV - EPG Card Programación" width="120">

</div>

> - 🔔 [What's On TV — Notify Card](https://github.com/janfajessen/What-s-On-TV-Search-and-Notify-Card/) — search programmes and set keyword alerts
<div align="center">
<img src="https://github.com/janfajessen/What-s-On-TV---EPG-TV-Guide/blob/c182f8324b4c54bc2a82bcd817de789b43c2208d/whatsontv_search_and_notify_card.png" alt="What's On TV - Search and Notify Card" width="130"><img src="https://github.com/janfajessen/What-s-On-TV---EPG-TV-Guide/blob/c182f8324b4c54bc2a82bcd817de789b43c2208d/whatsontv_search_and_notify_card_saved_watches.png" alt="What's On TV - Search and Notify Card saved watches" width="130">
</div>
---

## EPG Sources

| Key | Source | Notes |
|---|---|---|
| `epg_doblem` | EPG dobleM | Spain, updated 4×/day |
| `tdtchannels` | TDTChannels | Spain |
| `freeview_uk` | Freeview EPG | United Kingdom |
| `es`, `mx`, `de`, `fr`, `it`, `pt` … | iptv-epg.org | 79 countries |
| `custom` | Custom URL | Any XMLTV `.xml` or `.xml.gz` |



🌐 Custom URL (XMLTV .xml / .xml.gz)

---

## Requirements

- Home Assistant 2024.1+
- Python 3.12+

---
<br>
<sub> Wat is op televisie - ما هو على التلفزيون - Televiziyada nə var - Што па тэлевізары - Какво има по телевизията - Šta je na televiziji - Què hi ha a la televisió - Co je v televizi - Hvad er i fjernsynet - Was läuft im Fernsehen - Τι παίζει στην τηλεόραση - Kio estas en televido - Qué hay en la televisión - Zer dago telebistan - چه چیزی در تلویزیون است - Mitä televisiossa on - Quoi à la télévision - Que hai na televisión - מה יש בטלוויזיה - टेलीविजन पर क्या है - Što je na televiziji - Mi van a televízióban - Apa yang di televisi - Hvað er í sjónvarpinu - Cosa c'è in televisione - テレビでは何が - რა არის ტელევიზორში - Теледидарда не бар - 텔레비전에 무엇이 나오나요 - Ką per televizorių - Kas ir televīzijā - Wat is er op televisie - Hva er på fjernsynet - Qu'i a a la television - Co w telewizji - O que há na televisão - Ce este la televizor - Что по телевизору - Čo je v televízii - Kaj je na televiziji - Çfarë është në televizion - Шта је на телевизији - Vad är på tv - อะไรอยู่ในโทรทัศน์ - Televizyonda ne var - Що по телевізору - Có gì trên truyền hình - 电视上有什么 </sub>

---


<img src="https://github.com/janfajessen/What-s-On-TV-Search-and-Notify-Card/blob/297b38ed5f117f3e127bd9932c1b2c2dc41d6b9f/What's%20On%20TV.png" alt="What's On TV" width="120">


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
<td width="20%" align="left"><sub>🏝️ Caribbean **</sub></td>
<td width="20%" align="left"><sub>🇨🇱 Chile</sub></td>
<td width="20%" align="left"><sub>🇨🇳 中国 **</sub></td>
<td width="20%" align="left"><sub>🇨🇴 Colombia</sub></td>
</tr>
<tr>
<td width="20%" align="left"><sub>🇨🇷 Costa Rica</sub></td>
<td width="20%" align="left"><sub>🇨🇮 Côte d'Ivoire **</sub></td>
<td width="20%" align="left"><sub>🇭🇷 Hrvatska</sub></td>
<td width="20%" align="left"><sub>🇨🇿 Česká republika</sub></td>
<td width="20%" align="left"><sub>🇨🇾 Κύπρος / Kıbrıs *</sub></td>
</tr>
<tr>
<td width="20%" align="left"><sub>🇩🇰 Danmark</sub></td>
<td width="20%" align="left"><sub>🇩🇴 Rep. Dominicana</sub></td>
<td width="20%" align="left"><sub>🇪🇨 Ecuador</sub></td>
<td width="20%" align="left"><sub>🇪🇬 مصر</sub></td>
<td width="20%" align="left"><sub>🇸🇻 El Salvador</sub></td>
</tr>
<tr>
<td width="20%" align="left"><sub>🇪🇪 Eesti **</sub></td>
<td width="20%" align="left"><sub>🇫🇴 Færøerne / Føroyar *</sub></td>
<td width="20%" align="left"><sub>🇫🇮 Suomi / Finland</sub></td>
<td width="20%" align="left"><sub>🇫🇷 France</sub></td>
<td width="20%" align="left"><sub>🇬🇪 საქართველო</sub></td>
</tr>
<tr>
<td width="20%" align="left"><sub>🇩🇪 Deutschland</sub></td>
<td width="20%" align="left"><sub>🇬🇭 Ghana</sub></td>
<td width="20%" align="left"><sub>🇬🇷 Ελλάδα</sub></td>
<td width="20%" align="left"><sub>🇬🇹 Guatemala</sub></td>
<td width="20%" align="left"><sub>🇭🇳 Honduras</sub></td>
</tr>
<tr>
<td width="20%" align="left"><sub>🇭🇰 Hong Kong / 香港</sub></td>
<td width="20%" align="left"><sub>🇭🇺 Magyarország</sub></td>
<td width="20%" align="left"><sub>🇮🇪 Ireland / Éire **</sub></td>
<td width="20%" align="left"><sub>🇮🇸 Ísland</sub></td>
<td width="20%" align="left"><sub>🇮🇳 Bharat भारत</sub></td>
</tr>
<tr>
<td width="20%" align="left"><sub>🇮🇩 Indonesia</sub></td>
<td width="20%" align="left"><sub>🇮🇱 יִשְׂרָאֵל</sub></td>
<td width="20%" align="left"><sub>🇮🇹 Italia</sub></td>
<td width="20%" align="left"><sub>🇯🇲 Jamaica **</sub></td>
<td width="20%" align="left"><sub>🇯🇵 日本</sub></td>
</tr>
<tr>
<td width="20%" align="left"><sub>🇰🇿 Қазақстан *</sub></td>
<td width="20%" align="left"><sub>🇰🇪 Kenya **</sub></td>
<td width="20%" align="left"><sub>🇱🇻 Latvija</sub></td>
<td width="20%" align="left"><sub>🇱🇧 لبنان</sub></td>
<td width="20%" align="left"><sub>🇱🇮 Liechtenstein *</sub></td>
</tr>
<tr>
<td width="20%" align="left"><sub>🇱🇾 Libya / ليبيا **</sub></td>
<td width="20%" align="left"><sub>🇱🇹 Lietuva</sub></td>
<td width="20%" align="left"><sub>🇱🇺 Lëtzebuerg / Luxembourg / Luxemburg</sub></td>
<td width="20%" align="left"><sub>🇲🇴 Macao / 澳門 **</sub></td>
<td width="20%" align="left"><sub>🇲🇬 Madagasikara **</sub></td>
</tr>
<tr>
<td width="20%" align="left"><sub>🇲🇼 Malawi **</sub></td>
<td width="20%" align="left"><sub>🇲🇾 Bahasa Melayu</sub></td>
<td width="20%" align="left"><sub>🇲🇹 Malta</sub></td>
<td width="20%" align="left"><sub>🇲🇺 Mauritius **</sub></td>
<td width="20%" align="left"><sub>🇲🇽 México</sub></td>
</tr>
<tr>
<td width="20%" align="left"><sub>🇲🇰 Северна Македонија</sub></td>
<td width="20%" align="left"><sub>🇲🇳 Монгол **</sub></td>
<td width="20%" align="left"><sub>🇲🇪 Crna Gora / Črna Гора</sub></td>
<td width="20%" align="left"><sub>🇲🇦 المغرب</sub></td>
<td width="20%" align="left"><sub>🇲🇨 Monaco / Mónegue *</sub></td>
</tr>
<tr>
<td width="20%" align="left"><sub>🇲🇿 Moçambique **</sub></td>
<td width="20%" align="left"><sub>🇳🇦 Namibia **</sub></td>
<td width="20%" align="left"><sub>🇳🇱 Nederland</sub></td>
<td width="20%" align="left"><sub>🇳🇨 Nouvelle-Calédonie **</sub></td>
<td width="20%" align="left"><sub>🇳🇿 New Zealand / Aotearoa</sub></td>
</tr>
<tr>
<td width="20%" align="left"><sub>🇳🇮 Nicaragua</sub></td>
<td width="20%" align="left"><sub>🇳🇬 Nigeria</sub></td>
<td width="20%" align="left"><sub>🇳🇴 Norge / Noreg</sub></td>
<td width="20%" align="left"><sub>🇵🇰 Pakistan **</sub></td>
<td width="20%" align="left"><sub>🇵🇦 Panamá</sub></td>
</tr>
<tr>
<td width="20%" align="left"><sub>🇵🇾 Paraguay</sub></td>
<td width="20%" align="left"><sub>🇵🇪 Perú</sub></td>
<td width="20%" align="left"><sub>🇵🇭 Pilipinas</sub></td>
<td width="20%" align="left"><sub>🇵🇱 Polska</sub></td>
<td width="20%" align="left"><sub>🇵🇸 فلسطين *</sub></td>
</tr>
<tr>
<td width="20%" align="left"><sub>🇵🇹 Portugal</sub></td>
<td width="20%" align="left"><sub>🇵🇷 Puerto Rico *</sub></td>
<td width="20%" align="left"><sub>🇶🇦 قطر **</sub></td>
<td width="20%" align="left"><sub>🇷🇴 România</sub></td>
<td width="20%" align="left"><sub>🇷🇺 Россия</sub></td>
</tr>
<tr>
<td width="20%" align="left"><sub>🇷🇸 Gora / Црна Гора</sub></td>
<td width="20%" align="left"><sub>🇸🇲 San Marino *</sub></td>
<td width="20%" align="left"><sub>🏴󠁧󠁢󠁳󠁣󠁴󠁿 Scotland **</sub></td>
<td width="20%" align="left"><sub>🇸🇬 Singapore / 新加坡 / சிங்கப்பூர் / Singapura</sub></td>
<td width="20%" align="left"><sub>🇸🇰 Slovensko</sub></td>
</tr>
<tr>
<td width="20%" align="left"><sub>🇸🇮 Slovenija</sub></td>
<td width="20%" align="left"><sub>🇿🇦 South Africa</sub></td>
<td width="20%" align="left"><sub>🇰🇷 대한민국</sub></td>
<td width="20%" align="left"><sub>🇸🇪 Sverige</sub></td>
<td width="20%" align="left"><sub>🇨🇭 Schweiz / Suisse / Svizzera / Svizra</sub></td>
</tr>
<tr>
<td width="20%" align="left"><sub>🇹🇼 Taiwan / 臺灣</sub></td>
<td width="20%" align="left"><sub>🇹🇭 ประเทศไทย</sub></td>
<td width="20%" align="left"><sub>🇹🇷 Türkiye</sub></td>
<td width="20%" align="left"><sub>🇺🇬 Uganda</sub></td>
<td width="20%" align="left"><sub>🇺🇦 Украïна</sub></td>
</tr>
<tr>
<td width="20%" align="left"><sub>🇦🇪 Al-Imarat</sub></td>
<td width="20%" align="left"><sub>🇬🇧 United Kingdom / Cymru / Alba</sub></td>
<td width="20%" align="left"><sub>🇺🇸 United States</sub></td>
<td width="20%" align="left"><sub>🇺🇾 Uruguay</sub></td>
<td width="20%" align="left"><sub>🇺🇿 Oʻzbekiston **</sub></td>
</tr>
<tr>
<td width="20%" align="left"><sub>🇻🇦 Città del Vaticano *</sub></td>
<td width="20%" align="left"><sub>🇻🇪 Venezuela</sub></td>
<td width="20%" align="left"><sub>🇻🇳 Việt Nam</sub></td>
<td width="20%" align="left"><sub>🇿🇲 Zambia **</sub></td>
<td width="20%" align="left"><sub>🇿🇼 Zimbabwe</sub></td>
</tr>
</table>

<sub> * Channels available via regional EPG sources &nbsp;&nbsp; <br>
** Requires manual URL configuration — see EPG Sources section &nbsp;&nbsp; <br>
*** Not all sources have been individually verified</sub>

## 🌐 Manual EPG Sources (`**` countries)

The following countries require a custom URL. Go to **Settings → Devices & Services → What's On TV → Add Entry** and paste the URL in the *Custom URL* field.

> Source: [globetvapp/epg](https://github.com/globetvapp/epg) — updated daily at 03:00 UTC

<table border="0" cellspacing="0" cellpadding="6" width="100%">
<tr>
<td width="20%" align="left"><sub>🏝️ Caribbean</sub></td>
<td width="80%" align="left"><sub><code>https://raw.githubusercontent.com/globetvapp/epg/main/Caribbean/caribbean1.xml</code></sub></td>
</tr>
<tr>
<td width="20%" align="left"><sub>🇨🇳 中国 China</sub></td>
<td width="80%" align="left"><sub><code>https://raw.githubusercontent.com/globetvapp/epg/main/China/china1.xml</code></sub></td>
</tr>
<tr>
<td width="20%" align="left"><sub>🇨🇮 Côte d'Ivoire</sub></td>
<td width="80%" align="left"><sub><code>https://raw.githubusercontent.com/globetvapp/epg/main/Ivorycoast/ivorycoast1.xml</code></sub></td>
</tr>
<tr>
<td width="20%" align="left"><sub>🇪🇪 Eesti Estonia</sub></td>
<td width="80%" align="left"><sub><code>https://raw.githubusercontent.com/globetvapp/epg/main/Estonia/estonia1.xml</code></sub></td>
</tr>
<tr>
<td width="20%" align="left"><sub>🇮🇪 Ireland / Éire</sub></td>
<td width="80%" align="left"><sub><code>https://raw.githubusercontent.com/globetvapp/epg/main/Ireland/ireland1.xml</code></sub></td>
</tr>
<tr>
<td width="20%" align="left"><sub>🇯🇲 Jamaica</sub></td>
<td width="80%" align="left"><sub><code>https://raw.githubusercontent.com/globetvapp/epg/main/Jamaica/jamaica1.xml</code></sub></td>
</tr>
<tr>
<td width="20%" align="left"><sub>🇰🇪 Kenya</sub></td>
<td width="80%" align="left"><sub><code>https://raw.githubusercontent.com/globetvapp/epg/main/Kenya/kenya1.xml</code></sub></td>
</tr>
<tr>
<td width="20%" align="left"><sub>🇱🇾 Libya / ليبيا</sub></td>
<td width="80%" align="left"><sub><code>https://epg.pw/xmltv.html?lang=ar</code></sub></td>
</tr>
<tr>
<td width="20%" align="left"><sub>🇲🇴 Macao / 澳門</sub></td>
<td width="80%" align="left"><sub><code>https://raw.githubusercontent.com/globetvapp/epg/main/Macau/macau1.xml</code></sub></td>
</tr>
<tr>
<td width="20%" align="left"><sub>🇲🇬 Madagasikara</sub></td>
<td width="80%" align="left"><sub><code>https://raw.githubusercontent.com/globetvapp/epg/main/Madagascar/madagascar1.xml</code></sub></td>
</tr>
<tr>
<td width="20%" align="left"><sub>🇲🇼 Malawi</sub></td>
<td width="80%" align="left"><sub><code>https://raw.githubusercontent.com/globetvapp/epg/main/Malawi/malawi1.xml</code></sub></td>
</tr>
<tr>
<td width="20%" align="left"><sub>🇲🇺 Mauritius</sub></td>
<td width="80%" align="left"><sub><code>https://raw.githubusercontent.com/globetvapp/epg/main/Mauritius/mauritius1.xml</code></sub></td>
</tr>
<tr>
<td width="20%" align="left"><sub>🇲🇳 Монгол Mongolia</sub></td>
<td width="80%" align="left"><sub><code>https://raw.githubusercontent.com/globetvapp/epg/main/Mongolia/mongolia1.xml</code></sub></td>
</tr>
<tr>
<td width="20%" align="left"><sub>🇲🇿 Moçambique</sub></td>
<td width="80%" align="left"><sub><code>https://raw.githubusercontent.com/globetvapp/epg/main/Mozambique/mozambique1.xml</code></sub></td>
</tr>
<tr>
<td width="20%" align="left"><sub>🇳🇦 Namibia</sub></td>
<td width="80%" align="left"><sub><code>https://raw.githubusercontent.com/globetvapp/epg/main/Namibia/namibia1.xml</code></sub></td>
</tr>
<tr>
<td width="20%" align="left"><sub>🇳🇨 Nouvelle-Calédonie</sub></td>
<td width="80%" align="left"><sub><code>https://raw.githubusercontent.com/globetvapp/epg/main/Newcaledonia/newcaledonia1.xml</code></sub></td>
</tr>
<tr>
<td width="20%" align="left"><sub>🇵🇰 Pakistan</sub></td>
<td width="80%" align="left"><sub><code>https://raw.githubusercontent.com/globetvapp/epg/main/Pakistan/pakistan1.xml</code></sub></td>
</tr>
<tr>
<td width="20%" align="left"><sub>🇶🇦 قطر Qatar</sub></td>
<td width="80%" align="left"><sub><code>https://raw.githubusercontent.com/globetvapp/epg/main/Qatar/qatar1.xml</code></sub></td>
</tr>
<tr>
<td width="20%" align="left"><sub>🏴󠁧󠁢󠁳󠁣󠁴󠁿 Scotland</sub></td>
<td width="80%" align="left"><sub><code>https://raw.githubusercontent.com/globetvapp/epg/main/Scotland/scotland1.xml</code></sub></td>
</tr>
<tr>
<td width="20%" align="left"><sub>🇺🇿 Oʻzbekiston</sub></td>
<td width="80%" align="left"><sub><code>https://raw.githubusercontent.com/globetvapp/epg/main/Uzbekistan/uzbekistan1.xml</code></sub></td>
</tr>
<tr>
<td width="20%" align="left"><sub>🇿🇲 Zambia</sub></td>
<td width="80%" align="left"><sub><code>https://raw.githubusercontent.com/globetvapp/epg/main/Zambia/zambia1.xml</code></sub></td>
</tr>
</table>

---

<img src="https://github.com/janfajessen/What-s-On-TV-Search-and-Notify-Card/blob/b3645cf0af684bdde893675cb4c80660424873ba/home_assistant_logo.png" alt="Home Assistant" width="60">
  

---


*If this integration is useful to you, consider giving it a ⭐ on GitHub.*
Or consider supporting development!

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Donate-yellow?style=for-the-badge&logo=buymeacoffee)
](https://www.buymeacoffee.com/janfajessen) 
[![Patreon](https://img.shields.io/badge/Patreon-Support-red?style=for-the-badge&logo=patreon)](https://www.patreon.com/janfajessen)
</div>



## License

MIT — see [LICENSE](LICENSE)
