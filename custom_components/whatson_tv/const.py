"""Constantes para What's On TV EPG."""

DOMAIN = "whatson_tv"

def _epg(code, name, flag="🌐"):
    """Genera entrada de fuente para iptv-epg.org."""
    return {
        "name": f"{flag} {name}",
        "url": f"https://iptv-epg.org/files/epg-{code.lower()}.xml.gz",
    }

EPG_SOURCES = {
    "es_doblem": {
        "name": "🇪🇸 España — EPG dobleM (Movistar+, Orange, TDT, 7 días)",
        "url": "https://raw.githubusercontent.com/davidmuma/EPG_dobleM/master/guiatv.xml",
    },
    "es_tdt": {
        "name": "🇪🇸 España — TDT en abierto (TDTChannels)",
        "url": "https://www.tdtchannels.com/epg/TV.xml.gz",
    },
    "gb_freeview": {
        "name": "🇬🇧 United Kingdom — Freeview (7 días, regional)",
        "url": "https://raw.githubusercontent.com/dp247/Freeview-EPG/master/epg.xml",
    },
    "al": _epg("al","Albania","🇦🇱"),
    "ar": _epg("ar","Argentina","🇦🇷"),
    "am": _epg("am","Armenia","🇦🇲"),
    "au": _epg("au","Australia","🇦🇺"),
    "at": _epg("at","Austria","🇦🇹"),
    "by": _epg("by","Belarus","🇧🇾"),
    "be": _epg("be","Belgium","🇧🇪"),
    "bo": _epg("bo","Bolivia","🇧🇴"),
    "ba": _epg("ba","Bosnia & Herzegovina","🇧🇦"),
    "br": _epg("br","Brazil","🇧🇷"),
    "bg": _epg("bg","Bulgaria","🇧🇬"),
    "ca": _epg("ca","Canada","🇨🇦"),
    "cl": _epg("cl","Chile","🇨🇱"),
    "co": _epg("co","Colombia","🇨🇴"),
    "cr": _epg("cr","Costa Rica","🇨🇷"),
    "hr": _epg("hr","Croatia","🇭🇷"),
    "cz": _epg("cz","Czech Republic","🇨🇿"),
    "dk": _epg("dk","Denmark","🇩🇰"),
    "do": _epg("do","Dominican Republic","🇩🇴"),
    "ec": _epg("ec","Ecuador","🇪🇨"),
    "eg": _epg("eg","Egypt","🇪🇬"),
    "sv": _epg("sv","El Salvador","🇸🇻"),
    "fi": _epg("fi","Finland","🇫🇮"),
    "fr": _epg("fr","France","🇫🇷"),
    "ge": _epg("ge","Georgia","🇬🇪"),
    "de": _epg("de","Germany","🇩🇪"),
    "gh": _epg("gh","Ghana","🇬🇭"),
    "gr": _epg("gr","Greece","🇬🇷"),
    "gt": _epg("gt","Guatemala","🇬🇹"),
    "hn": _epg("hn","Honduras","🇭🇳"),
    "hk": _epg("hk","Hong Kong","🇭🇰"),
    "hu": _epg("hu","Hungary","🇭🇺"),
    "is": _epg("is","Iceland","🇮🇸"),
    "in": _epg("in","India","🇮🇳"),
    "id": _epg("id","Indonesia","🇮🇩"),
    "il": _epg("il","Israel","🇮🇱"),
    "it": _epg("it","Italy","🇮🇹"),
    "jp": _epg("jp","Japan","🇯🇵"),
    "lv": _epg("lv","Latvia","🇱🇻"),
    "lb": _epg("lb","Lebanon","🇱🇧"),
    "lt": _epg("lt","Lithuania","🇱🇹"),
    "lu": _epg("lu","Luxembourg","🇱🇺"),
    "mk": _epg("mk","Macedonia","🇲🇰"),
    "my": _epg("my","Malaysia","🇲🇾"),
    "mt": _epg("mt","Malta","🇲🇹"),
    "mx": _epg("mx","Mexico","🇲🇽"),
    "me": _epg("me","Montenegro","🇲🇪"),
    "ma": _epg("ma","Morocco","🇲🇦"),
    "nl": _epg("nl","Netherlands","🇳🇱"),
    "nz": _epg("nz","New Zealand","🇳🇿"),
    "ni": _epg("ni","Nicaragua","🇳🇮"),
    "ng": _epg("ng","Nigeria","🇳🇬"),
    "no": _epg("no","Norway","🇳🇴"),
    "pa": _epg("pa","Panama","🇵🇦"),
    "py": _epg("py","Paraguay","🇵🇾"),
    "pe": _epg("pe","Peru","🇵🇪"),
    "ph": _epg("ph","Philippines","🇵🇭"),
    "pl": _epg("pl","Poland","🇵🇱"),
    "pt": _epg("pt","Portugal","🇵🇹"),
    "pr": _epg("pr","Puerto Rico","🇵🇷"),
    "ro": _epg("ro","Romania","🇷🇴"),
    "ru": _epg("ru","Russia","🇷🇺"),
    "rs": _epg("rs","Serbia","🇷🇸"),
    "sg": _epg("sg","Singapore","🇸🇬"),
    "sk": _epg("sk","Slovakia","🇸🇰"),
    "si": _epg("si","Slovenia","🇸🇮"),
    "za": _epg("za","South Africa","🇿🇦"),
    "kr": _epg("kr","South Korea","🇰🇷"),
    "es": _epg("es","Spain (iptv-epg.org)","🇪🇸"),
    "se": _epg("se","Sweden","🇸🇪"),
    "ch": _epg("ch","Switzerland","🇨🇭"),
    "tw": _epg("tw","Taiwan","🇹🇼"),
    "th": _epg("th","Thailand","🇹🇭"),
    "tr": _epg("tr","Turkey","🇹🇷"),
    "ua": _epg("ua","Ukraine","🇺🇦"),
    "ae": _epg("ae","United Arab Emirates","🇦🇪"),
    "gb": _epg("gb","United Kingdom (iptv-epg.org)","🇬🇧"),
    "us": _epg("us","United States","🇺🇸"),
    "uy": _epg("uy","Uruguay","🇺🇾"),
    "ve": _epg("ve","Venezuela","🇻🇪"),
    "vn": _epg("vn","Vietnam","🇻🇳"),
    "custom": {
        "name": "🌐 Custom URL (XMLTV .xml / .xml.gz)",
        "url": "",
    },
}

DEFAULT_SOURCE     = "es_doblem"
DEFAULT_SCAN_INTERVAL = 12
MIN_SCAN_INTERVAL  = 1
MAX_SCAN_INTERVAL  = 24

CONF_EPG_SOURCE    = "epg_source"
CONF_EPG_URL       = "epg_url"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_CHANNELS      = "channels"

ATTR_CHANNEL_ID       = "channel_id"
ATTR_CHANNEL_NAME     = "channel_name"
ATTR_CHANNEL_ICON     = "channel_icon"
ATTR_CURRENT_TITLE    = "titulo"
ATTR_CURRENT_START    = "inicio"
ATTR_CURRENT_END      = "fin"
ATTR_CURRENT_DESC     = "descripcion"
ATTR_CURRENT_ICON     = "imagen"
ATTR_CURRENT_PROGRESS = "progreso_pct"
ATTR_NEXT_TITLE       = "siguiente_titulo"
ATTR_NEXT_START       = "siguiente_inicio"
ATTR_NEXT_END         = "siguiente_fin"
ATTR_NEXT_DESC        = "siguiente_descripcion"
ATTR_SCHEDULE         = "programacion"
MAX_SCHEDULE_ITEMS    = 50
