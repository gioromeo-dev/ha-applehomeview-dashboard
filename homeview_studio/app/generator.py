"""Build the Home View Lovelace config from base.json + a user layout (layout.json)."""
import copy
import json
import os
import re

CLOCK_JS = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "clock.js"), encoding="utf-8").read()
FACES_JS = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "faces.js"), encoding="utf-8").read()
FACE_IDS = ["clock", "photos", "flow", "meridian", "weather", "calendar"]
PHOTO_DIR = "media-source://media_source/local/Photo Slideshow"
CLOCK_STYLES = ["original", "classic", "minimal", "bold", "digital", "stacked", "solar"]
SCREEN_W = "Math.max(100, 100 * (((window.innerWidth || 1180) - 28) / ((window.innerHeight || 820) - 28)))"


def clock_js(style, acc, fg, w="100", bg=False):
    return ("[[[\nconst d = new Date();\nconst STYLE = %s, ACC = %s, FG = %s, BG = %s;\nconst W = %s;\n%s\n]]]"
            % (json.dumps(style), json.dumps(acc), json.dumps(fg), "true" if bg else "false", w, CLOCK_JS))

FONT = "-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text', 'Helvetica Neue', Helvetica, Roboto, sans-serif"

# Values baked into base.json that the layout can override.
BASE_WEATHER = "weather.home"
BASE_CAMERA = "camera.homeview"
BASE_DOORBELL = "event.homeview_doorbell"
BASE_ACCENT = "#4D7DB8"
BASE_BG = "/local/homeview/studio/aurora-light.jpg"
BASE_CAL = "calendar.homeview"
BASE_URL = "home-view"

ON_STATES = ["on", "playing", "unlocked", "open", "opening", "cleaning", "returning", "paused",
             "cool", "dry", "fan_only", "heat", "heat_cool", "auto", "home"]

EXTRA_TEMPLATES = {
    "hv_door_tile": {
        "template": "glass_tile",
        "label": "[[[ if (!entity || entity.state === 'unavailable') return 'Non risponde'; return entity.state === 'on' ? 'Aperta' : 'Chiusa'; ]]]",
        "icon": "[[[ const dc = entity && entity.attributes.device_class; const open = entity && entity.state === 'on'; if (dc === 'window') return open ? 'mdi:window-open-variant' : 'mdi:window-closed-variant'; if (dc === 'garage_door') return open ? 'mdi:garage-open' : 'mdi:garage'; return open ? 'mdi:door-open' : 'mdi:door-closed'; ]]]",
    },
    "hv_climate_tile": {
        "template": "glass_tile",
        "label": "[[[ if (!entity) return ''; const m = {off:'Spento', cool:'Raffredda', dry:'Deumidifica', fan_only:'Ventola', heat:'Riscalda', heat_cool:'Auto', auto:'Auto', unavailable:'Non risponde'}; let s = m[entity.state] || entity.state; if (entity.state !== 'off' && entity.attributes.temperature) s = entity.attributes.temperature + '° · ' + s; return s; ]]]",
    },
    "hv_media_tile": {
        "template": "glass_tile",
        "label": "[[[ if (!entity) return ''; const m = {off:'Spento', standby:'Spento', idle:'Inattivo', on:'Acceso', paused:'In pausa', unavailable:'Non risponde'}; if (entity.state === 'playing') return entity.attributes.media_title || 'In riproduzione'; return m[entity.state] || entity.state; ]]]",
    },
    "hv_sensor_tile": {
        "template": "glass_tile",
        "label": "[[[ if (!entity || entity.state === 'unavailable') return 'Non risponde'; const u = entity.attributes.unit_of_measurement; const n = Number(entity.state); const v = isNaN(n) ? entity.state : (Math.round(n * 10) / 10).toLocaleString('it-IT'); return u ? v + (u === '%' || u.startsWith('°') ? '' : ' ') + u : v; ]]]",
    },
    "hv_cover_tile": {
        "template": "glass_tile",
        "label": "[[[ if (!entity) return ''; const m = {open:'Aperta', closed:'Chiusa', opening:'In apertura', closing:'In chiusura', unavailable:'Non risponde'}; const p = entity.attributes.current_position; return (m[entity.state] || entity.state) + (p != null && entity.state === 'open' ? ' · ' + p + '%' : ''); ]]]",
    },
    "hv_lock_tile": {
        "template": "glass_tile",
        "label": "[[[ if (!entity) return ''; const m = {locked:'Chiusa', unlocked:'Aperta', locking:'Chiusura…', unlocking:'Apertura…', jammed:'Bloccata', unavailable:'Non risponde'}; return m[entity.state] || entity.state; ]]]",
        "icon": "[[[ return entity && entity.state === 'unlocked' ? 'mdi:lock-open-variant-outline' : 'mdi:lock-outline'; ]]]",
    },
    "hv_state_tile": {
        "template": "glass_tile",
        "label": "[[[ if (!entity) return ''; const m = {on:'Acceso', off:'Spento', open:'Aperto', closed:'Chiuso', home:'A casa', not_home:'Fuori', unavailable:'Non risponde', unknown:'—', idle:'Inattivo', playing:'In riproduzione', paused:'In pausa', armed_away:'Inserito', armed_home:'Inserito (casa)', disarmed:'Disinserito', triggered:'Allarme!'}; const u = entity.attributes.unit_of_measurement; return m[entity.state] || (entity.state + (u ? ' ' + u : '')); ]]]",
    },
}

UNIVERSAL_LABEL = ("[[[ if (!entity) return 'Entità non trovata'; const s = entity.state, a = entity.attributes, d = entity.entity_id.split('.')[0];"
    " if (s === 'unavailable') return 'Non risponde';"
    " if (d === 'light') return s === 'on' ? (a.brightness ? 'Accesa · ' + Math.round(a.brightness / 2.55) + '%' : 'Accesa') : 'Spenta';"
    " if (d === 'climate') { const m = {off:'Spento', cool:'Raffredda', dry:'Deumidifica', fan_only:'Ventola', heat:'Riscalda', heat_cool:'Auto', auto:'Auto'}; let r = m[s] || s; if (s !== 'off' && a.temperature) r = a.temperature + '° · ' + r; return r; }"
    " if (d === 'media_player') { if (s === 'playing') return a.media_title || 'In riproduzione'; return {off:'Spento', standby:'Spento', idle:'Inattivo', on:'Acceso', paused:'In pausa'}[s] || s; }"
    " if (d === 'sensor') { const u = a.unit_of_measurement; const n = Number(s); const v = isNaN(n) ? s : (Math.round(n * 10) / 10).toLocaleString('it-IT'); return u ? v + (u === '%' || u.startsWith('°') ? '' : ' ') + u : v; }"
    " if (d === 'binary_sensor' && ['door','window','garage_door','opening'].includes(a.device_class)) return s === 'on' ? 'Aperta' : 'Chiusa';"
    " if (d === 'cover') return ({open:'Aperta', closed:'Chiusa', opening:'In apertura', closing:'In chiusura'}[s] || s) + (a.current_position != null && s === 'open' ? ' · ' + a.current_position + '%' : '');"
    " if (d === 'lock') return {locked:'Chiusa', unlocked:'Aperta', jammed:'Bloccata'}[s] || s;"
    " if (d === 'scene' || d === 'script') return 'Tocca per attivare';"
    " return {on:'Acceso', off:'Spento', open:'Aperto', closed:'Chiuso', home:'A casa', not_home:'Fuori', unknown:'—', idle:'Inattivo'}[s] || (s + (a.unit_of_measurement ? ' ' + a.unit_of_measurement : '')); ]]]")

GROUP_LABEL = ("[[[ const ids = (variables && variables.members) || []; const on = ['on','playing','unlocked','open','opening','cool','dry','fan_only','heat','heat_cool','auto','home'];"
    " const sts = ids.map(i => states[i]).filter(Boolean); if (!sts.length) return 'Vuoto';"
    " const n = sts.filter(s => on.includes(s.state)).length; if (variables.label) return variables.label;"
    " if (!n) return sts.length === 1 ? 'Spento' : 'Tutto spento'; if (n === sts.length && n > 1) return 'Tutti accesi';"
    " return n + (n === 1 ? ' acceso' : ' accesi') + ' su ' + sts.length; ]]]")
GROUP_ANY_ON = ("[[[ const ids = (variables && variables.members) || []; const on = ['on','playing','unlocked','open','opening','cool','dry','fan_only','heat','heat_cool','auto','home'];"
    " return ids.some(i => states[i] && on.includes(states[i].state)); ]]]")
GROUP_HOLD = ("[[[ const ids = (variables && variables.members) || []; const tg = ids.filter(i => ['light','switch','fan','input_boolean','cover','media_player','climate','automation','humidifier','siren'].includes(i.split('.')[0]));"
    " if (!tg.length) return; const on = ['on','playing','open','opening','cool','dry','fan_only','heat','heat_cool','auto'];"
    " const any = tg.some(i => states[i] && on.includes(states[i].state));"
    " hass.callService('homeassistant', any ? 'turn_off' : 'turn_on', {entity_id: tg}); ]]]")

EXTRA_TEMPLATES["hv_pop_member"] = {"template": "hw_pop_btn", "label": UNIVERSAL_LABEL, "hold_action": {"action": "more-info"}}
EXTRA_TEMPLATES["hv_group_tile"] = {"template": "glass_tile", "show_label": True, "label": GROUP_LABEL, "variables": {"members": [], "label": ""},
                                   "hold_action": {"action": "javascript", "javascript": GROUP_HOLD, "haptic": "heavy"}}

STYLE_CHOICES = ["glass_tile", "hw_fan_tile", "hv_door_tile", "hv_climate_tile", "hv_media_tile",
                 "hv_sensor_tile", "hv_cover_tile", "hv_lock_tile", "hv_state_tile"]

TOGGLE_DOMAINS = {"light", "switch", "input_boolean", "fan", "cover", "automation", "siren", "humidifier"}
OPENING_CLASSES = {"door", "window", "garage_door", "opening"}


def auto_template(entity_id, device_class=None, icon=None):
    dom = entity_id.split(".", 1)[0]
    if dom == "fan" or (dom == "switch" and icon and "fan" in icon):
        return "hw_fan_tile"
    if dom in ("light", "switch", "input_boolean", "scene", "script", "automation", "siren", "humidifier"):
        return "glass_tile"
    if dom == "binary_sensor":
        return "hv_door_tile" if device_class in OPENING_CLASSES else "hv_state_tile"
    return {"climate": "hv_climate_tile", "media_player": "hv_media_tile", "sensor": "hv_sensor_tile",
            "cover": "hv_cover_tile", "lock": "hv_lock_tile"}.get(dom, "hv_state_tile")


def auto_tap(entity_id):
    dom = entity_id.split(".", 1)[0]
    if dom in ("scene", "script"):
        return {"action": "perform-action", "perform_action": f"{dom}.turn_on",
                "target": {"entity_id": entity_id}, "haptic": "success"}
    if dom in TOGGLE_DOMAINS:
        return {"action": "toggle", "haptic": "light"}
    return {"action": "more-info"}


def hex_rgb(h):
    h = (h or "#FFFFFF").lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    try:
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        return (255, 255, 255)


def rgba(h, a):
    r, g, b = hex_rgb(h)
    return f"rgba({r},{g},{b},{round(max(0.0, min(1.0, a)), 3)})"


def set_style(lst, key, value):
    """Set `key` in a button-card style list ([{k: v}, ...]), replacing any existing entry."""
    for item in lst:
        if key in item:
            item[key] = value
            return
    lst.append({key: value})


def find_view(d, path):
    return next((v for v in d["views"] if v.get("path") == path), None)


def deep_merge(dst, src):
    for k, v in src.items():
        if isinstance(v, dict) and isinstance(dst.get(k), dict):
            deep_merge(dst[k], v)
        else:
            dst[k] = v
    return dst


DEFAULT_LAYOUT = {
    "version": 1,
    "language": "auto",
    "dashboard": {"url_path": "home-view", "title": "Home View"},
    "grid": {"columns": 5, "calendar_bar": True},
    "tiles": [
        {"kind": "weather", "x": 0, "y": 0, "w": 2, "h": 2},
        {"kind": "clock", "x": 2, "y": 0, "w": 1, "h": 1},
    ],
    "theme": {
        "background": BASE_BG,
        "background_opacity": 100,
        "accent": BASE_ACCENT,
        "tile_opacity": 0.16,
        "tile_on_color": "#FFFFFF",
        "tile_on_opacity": 0.62,
        "text_color": "#FFFFFF",
        "text_on_color": "#1C1C1E",
        "radius": 24,
        "blur": 12,
        "gap": 16,
        "name_size": 20,
        "label_size": 15,
        "icon_size": 34,
        "max_width": 1400,
        "shadow": True,
        "background_dark": "",
        "clock_home": "original",
        "clock_widgets": "original",
        "clock_screensaver": "original",
        "screensaver_text": "#0B0B0C",
    },
    "behavior": {
        "screensaver": True,
        "idle_time": 120,
        "fullscreen": False,
        "hide_toolbar": False,
        "hide_sidebar": False,
        "mouse_swipe": True,
        "swipe_animation": "swipe",
        "swipe_wrap": True,
        "kiosk_always": False,
        "hold_action": "more-info",
        "haptic": True,
        "faces": ["clock"],
        "face_interval": 60,
        "photo_folder": True,
        "photo_interval": 20,
        "motion_entity": "",
        "night_mode": False,
        "night_start": "22:30",
        "night_end": "07:00",
        "night_dim": 0.35,
        "show_widgets": True,
        "show_cameras": True,
    },
    "sources": {
        "weather": BASE_WEATHER,
        "calendars": [],
        "camera": BASE_CAMERA,
        "doorbell": BASE_DOORBELL,
        "cameras": [BASE_CAMERA],
    },
}


def normalize(layout):
    out = copy.deepcopy(DEFAULT_LAYOUT)
    if layout:
        tiles = layout.get("tiles")
        deep_merge(out, {k: v for k, v in layout.items() if k != "tiles"})
        if tiles is not None:
            out["tiles"] = tiles
    return out


def _replace_entity(text, old, new):
    if not new or new == old:
        return text
    return re.sub(re.escape(old) + r"(?![A-Za-z0-9_])", new, text)


def _cal_js(cals, with_name=True):
    parts = []
    for c in cals:
        name = (c.get("name") or c["entity"]).replace("'", "\\'")
        col = c.get("color") or "#FF9F0A"
        parts.append(f"'{c['entity']}': {{name: '{name}', color: '{col}'}}" if with_name
                     else f"'{c['entity']}': {{color: '{col}'}}")
    return "{" + ", ".join(parts) + "}"


def build_tile(t, base_cam, main_camera, beh, info=None):
    kind = t.get("kind", "entity")
    if kind == "weather":
        return {"type": "custom:button-card", "template": "hw_weather"}
    if kind == "clock":
        return {"type": "custom:button-card", "template": "hw_clock"}
    if kind == "camera":
        c = copy.deepcopy(base_cam)
        ent = t.get("entity") or main_camera
        c["entity"] = ent
        c["name"] = t.get("name") or "Telecamera"
        c["label"] = t.get("label") or "Live"
        if ent != main_camera:
            c["tap_action"] = {"action": "more-info"}
        return c

    if kind == "group":
        members = [m for m in (t.get("entities") or []) if m]
        c = {"type": "custom:button-card", "template": "hv_group_tile", "name": t.get("name") or "Gruppo",
             "icon": t.get("icon") or "mdi:lightbulb-group-outline",
             "variables": {"members": members, "label": t.get("label") or ""},
             "triggers_update": members or "all",
             "tap_action": {"action": "navigate", "navigation_path": t["_hash"]}}
        if t.get("hold", "toggle_all") != "toggle_all":
            c["hold_action"] = {"action": "none"}
        return c

    ent = t.get("entity", "")
    style = t.get("style") or "auto"
    if style == "auto":
        meta = (info or {}).get(ent, {})
        style = auto_template(ent, t.get("device_class") or meta.get("device_class"), t.get("icon") or meta.get("icon"))
    c = {"type": "custom:button-card", "template": style, "entity": ent}
    if t.get("name"):
        c["name"] = t["name"]
    if t.get("label"):
        c["label"] = t["label"]
    elif style == "glass_tile" and ent.startswith(("scene.", "script.")):
        c["label"] = "Scena" if ent.startswith("scene.") else "Script"
    if t.get("icon"):
        c["icon"] = t["icon"]
    tap = t.get("tap") or "auto"
    if tap == "auto":
        c["tap_action"] = auto_tap(ent)
    elif tap == "navigate":
        c["tap_action"] = {"action": "navigate", "navigation_path": t.get("navigation_path") or "#"}
    else:
        c["tap_action"] = {"action": tap}
    if not beh.get("haptic", True):
        c["tap_action"].pop("haptic", None)
    return c


TOGGLEABLE = ("light", "switch", "fan", "input_boolean", "cover", "media_player", "climate", "automation", "humidifier", "siren")


def group_popup(t, cal_popup, beh, info):
    if not cal_popup:
        return None
    members = [m for m in (t.get("entities") or []) if m]
    p = copy.deepcopy({k: v for k, v in cal_popup.items() if k not in ("cards", "entity")})
    p["hash"] = t["_hash"]
    p["name"] = t.get("name") or "Gruppo"
    p["icon"] = t.get("icon") or "mdi:lightbulb-group-outline"
    p["styles"] = p.get("styles", "").replace("* 0.90)", "* 0.72)")
    p["width_desktop"] = p.get("width_desktop", "").replace("* 0.90)", "* 0.72)")
    cards = []
    for m in members:
        dom = m.split(".", 1)[0]
        c = {"type": "custom:button-card", "template": "hv_pop_member", "entity": m}
        tm = (t.get("names") or {}).get(m)
        if tm:
            c["name"] = tm
        if dom in ("scene", "script"):
            c["tap_action"] = {"action": "perform-action", "perform_action": f"{dom}.turn_on", "target": {"entity_id": m}}
        elif dom in TOGGLEABLE and dom not in ("climate", "media_player"):
            c["tap_action"] = {"action": "toggle", "haptic": "light"}
        else:
            c["tap_action"] = {"action": "more-info"}
        cards.append(c)
    if not cards:
        cards.append({"type": "custom:button-card", "template": "hw_pop_btn", "name": "Gruppo vuoto",
                      "label": "Aggiungi dispositivi da Home View Studio", "icon": "mdi:information-outline",
                      "tap_action": {"action": "none"}})
    stackc = [{"type": "grid", "columns": 2 if len(cards) <= 4 else 3, "square": False, "cards": cards}]
    tg = [m for m in members if m.split(".", 1)[0] in TOGGLEABLE]
    if tg:
        stackc.append({"type": "grid", "columns": 2, "square": False, "cards": [
            {"type": "custom:button-card", "template": "hw_pop_btn", "name": "Accendi tutto", "icon": "mdi:power",
             "label": f"{len(tg)} dispositivi", "tap_action": {"action": "perform-action", "perform_action": "homeassistant.turn_on",
                                                               "target": {"entity_id": tg}, "haptic": "success"}},
            {"type": "custom:button-card", "template": "hw_pop_btn", "name": "Spegni tutto", "icon": "mdi:power-off",
             "label": f"{len(tg)} dispositivi", "tap_action": {"action": "perform-action", "perform_action": "homeassistant.turn_off",
                                                               "target": {"entity_id": tg}, "haptic": "success"}},
        ]})
    p["cards"] = [{"type": "vertical-stack", "cards": stackc}]
    return p


def build_cameras(d, cams, info):
    camv = find_view(d, "cameras")
    if not camv:
        return
    cstack = camv["cards"][0]["cards"]
    grid = cstack[0]
    base_c1 = grid["custom_fields"]["c1"]["card"]
    base_pop = next((c for c in cstack if c.get("hash") == "#cam1"), None)
    n = len(cams)
    cols = 1 if n == 1 else 2 if n <= 4 else 3
    rows = -(-n // cols)
    gap = 12
    cf, cfs, pops = {}, {}, []
    for i, ent in enumerate(cams):
        key = f"c{i + 1}"
        c = copy.deepcopy(base_c1)
        c["entity"] = ent
        c["name"] = (info or {}).get(ent, {}).get("name") or ent.split(".", 1)[1].replace("_", " ").title()
        c["tap_action"] = {"action": "navigate", "navigation_path": f"#cam{i + 1}", "haptic": "light"}
        if n > 1:
            h = f"calc((100vh - 28px - {(rows - 1) * gap}px) / {rows})"
            c["styles"]["card"] = [{"width": f"min(100%, calc({h} * 1.7778))"}, {"height": "auto"},
                                   {"aspect-ratio": "16 / 9"}, {"max-width": "none"}]
        cf[key] = {"card": c}
        cfs[key] = [{"justify-self": "center"}, {"align-self": "center"}, {"min-width": "0"}, {"width": "100%"},
                    {"display": "flex"}, {"justify-content": "center"}]
        if base_pop:
            p = copy.deepcopy(base_pop)
            p["hash"] = f"#cam{i + 1}"
            p["name"] = c["name"]

            def setc(cards):
                for x in cards:
                    if x.get("type") == "picture-entity":
                        x["entity"] = ent
                    if "cards" in x:
                        setc(x["cards"])
            setc(p.get("cards", []))
            pops.append(p)
    cells = [f"c{i + 1}" for i in range(n)] + ["."] * (rows * cols - n)
    areas = " ".join('"' + " ".join(cells[r * cols:(r + 1) * cols]) + '"' for r in range(rows))
    grid["custom_fields"] = cf
    grid["styles"]["custom_fields"] = cfs
    grid["styles"]["grid"] = [g for g in grid["styles"]["grid"]
                              if not any(k in g for k in ("grid-template-areas", "grid-template-columns", "grid-template-rows", "gap"))]
    grid["styles"]["grid"] += [{"grid-template-areas": areas}, {"grid-template-columns": f"repeat({cols}, minmax(0, 1fr))"},
                               {"grid-template-rows": " ".join(["auto"] * rows)}, {"gap": f"{gap}px"}]
    camv["cards"][0]["cards"] = [grid] + pops


# ---------------------------------------------------------------- English dashboard
# The base and the templates are written in Italian; for English we translate the
# exact JS/JSON tokens (quoted), so user-entered names are left alone.
EN_TARGETED = [
    ("locked:'Chiusa', unlocked:'Aperta'", "locked:'Locked', unlocked:'Unlocked'"),
    ("' acceso' : ' accesi') + ' su '", "' on' : ' on') + ' of '"),
    ("'Oggi' : diff === 1 ? 'Domani'", "'Today' : diff === 1 ? 'Tomorrow'"),
    ("i === 0 ? 'Ora'", "i === 0 ? 'Now'"),
    ("'Accesa · '", "'On · '"),
    ("'it-IT'", "'en-US'"),
    (">Casa<", ">Home<"),
    (">Prossimi<", ">Up next<"),
    (">Prossime 12 ore<", ">Next 12 hours<"),
    (">Alba<", ">Sunrise<"), (">Tramonto<", ">Sunset<"),
    ("Carico il calendario", "Loading calendar"),
    ("Calendario non disponibile: ", "Calendar unavailable: "),
    ("Nessun impegno questa settimana", "Nothing on the calendar this week"),
    ("Meteo non disponibile", "Weather unavailable"),
    ("Previsioni non disponibili: ", "Forecast unavailable: "),
    ("Nessuna foto nella cartella Photo Slideshow", "No photos in the Photo Slideshow folder yet"),
    ("Carico le foto", "Loading photos"),
    ("Aggiungi dispositivi da Home View Studio", "Add devices in Home View Studio"),
]
EN_WORDS = {  # quoted tokens: 'x' in JS and "x" as JSON values
    "Tutto il giorno": "All day", "OGGI": "TODAY", "Umidità": "Humidity", "Vento": "Wind", "Pressione": "Pressure",
    "Visibilità": "Visibility", "Punto di rugiada": "Dew point", "Indice UV": "UV index",
    "Sereno": "Clear", "Nuvoloso": "Cloudy", "Allerta": "Warning", "Nebbia": "Fog", "Grandine": "Hail", "Temporale": "Thunderstorm",
    "Poco nuvoloso": "Partly cloudy", "Pioggia forte": "Pouring", "Pioggia": "Rain", "Neve": "Snow", "Nevischio": "Sleet",
    "Soleggiato": "Sunny", "Ventoso": "Windy",
    "Non risponde": "Not responding", "Aperta": "Open", "Chiusa": "Closed", "Aperto": "Open", "Chiuso": "Closed",
    "Spento": "Off", "Spenta": "Off", "Acceso": "On", "Accesa": "On", "Raffredda": "Cooling", "Deumidifica": "Drying",
    "Ventola": "Fan", "Riscalda": "Heating", "Inattivo": "Idle", "In pausa": "Paused", "In riproduzione": "Playing",
    "In apertura": "Opening", "In chiusura": "Closing", "Chiusura…": "Locking…", "Apertura…": "Unlocking…", "Bloccata": "Jammed",
    "A casa": "Home", "Fuori": "Away", "Inserito": "Armed", "Inserito (casa)": "Armed (home)", "Disinserito": "Disarmed",
    "Allarme!": "Triggered!", "Tocca per attivare": "Tap to activate", "Entità non trovata": "Entity not found",
    "Vuoto": "Empty", "Tutto spento": "All off", "Tutti accesi": "All on",
    "Accendi tutto": "Turn all on", "Spegni tutto": "Turn all off", "Gruppo vuoto": "Empty group", "Gruppo": "Group",
    "Scena": "Scene", "Meteo": "Weather", "Calendario": "Calendar", "Campanello": "Doorbell", "Telecamera": "Camera",
}


def to_english(d):
    text = json.dumps(d, ensure_ascii=False)
    for a, b in EN_TARGETED:
        text = text.replace(a, b)
    for it, en in sorted(EN_WORDS.items(), key=lambda kv: -len(kv[0])):
        text = text.replace(f"'{it}'", f"'{en}'").replace(f'"{it}"', f'"{en}"')
    text = re.sub(r'"(\d+) dispositivi"', r'"\1 devices"', text)
    return json.loads(text)


def faces_js(cfg):
    return ("[[[\nconst d = new Date();\nconst CFG = %s;\n"
            "CFG.aspect = ((window.innerWidth || 1180) - 28) / ((window.innerHeight || 820) - 28);\n"
            "const CLOCK = (d, STYLE, ACC, FG, W, BG) => {\n%s\n};\n%s\n]]]"
            % (json.dumps(cfg, ensure_ascii=False), CLOCK_JS, FACES_JS))


def generate(base, layout, info=None, lang=None, wallpapers=None):
    """info: optional {entity_id: {device_class, icon}} used for automatic tile styles."""
    L = normalize(layout)
    src, th, beh, dash = L["sources"], L["theme"], L["behavior"], L["dashboard"]
    if info:  # fall back to entities that really exist on this Home Assistant
        def first(domain):
            return next((e for e in sorted(info) if e.startswith(domain + ".")), None)
        if src.get("weather") not in info:
            src["weather"] = first("weather") or src.get("weather")
        if src.get("camera") not in info:
            src["camera"] = first("camera") or src.get("camera")
        src["cameras"] = [c for c in (src.get("cameras") or []) if c in info] or ([src["camera"]] if src.get("camera") in info else [])
        cl = [c for c in (src.get("calendars") or []) if c.get("entity") in info]
        src["calendars"] = cl or [{"entity": e, "name": (info[e].get("name") or e), "color": "#FF9F0A"}
                                  for e in sorted(info) if e.startswith("calendar.")][:3]
    url = (dash.get("url_path") or BASE_URL).strip("/")

    # ---------- global text substitutions (entities baked into JS) ----------
    text = json.dumps(base, ensure_ascii=False)
    text = _replace_entity(text, BASE_WEATHER, src.get("weather"))
    text = _replace_entity(text, BASE_DOORBELL, src.get("doorbell"))
    text = _replace_entity(text, BASE_CAMERA, src.get("camera"))
    text = text.replace(BASE_ACCENT, th.get("accent") or BASE_ACCENT)
    text = text.replace(f"/{BASE_URL}/", f"/{url}/")
    cals = [c for c in src.get("calendars") or [] if c.get("entity")]
    if cals:
        text = text.replace("{'calendar.homeview': {name: 'Calendario', color: '#FF9F0A'}}", _cal_js(cals))
        text = text.replace("{'calendar.homeview': {color: '#FF9F0A'}}", _cal_js(cals, False))
    d = json.loads(text)
    if cals:
        ids = [c["entity"] for c in cals]

        def fix_cal(o):
            if isinstance(o, dict):
                for k, v in o.items():
                    if isinstance(v, list) and BASE_CAL in v:
                        o[k] = [x for y in v for x in (ids if y == BASE_CAL else [y])]
                    elif v == BASE_CAL:
                        o[k] = ids[0]
                    else:
                        fix_cal(v)
            elif isinstance(o, list):
                for i in o:
                    fix_cal(i)
        fix_cal(d)

    tpl = d["button_card_templates"]
    for k, v in EXTRA_TEMPLATES.items():
        tpl[k] = copy.deepcopy(v)

    # ---------- theme: glass tiles ----------
    g = tpl["glass_tile"]
    card = g["styles"]["card"]
    a = float(th.get("tile_opacity", 0.16))
    set_style(card, "border-radius", f"{int(th.get('radius', 24))}px")
    set_style(card, "background", f"linear-gradient(135deg, {rgba('#FFFFFF', a)} 0%, {rgba('#FFFFFF', a * 0.31)} 50%, {rgba('#FFFFFF', a * 0.19)} 100%)")
    blur = int(th.get("blur", 12))
    set_style(card, "backdrop-filter", f"blur({blur}px) saturate(110%)" if blur else "none")
    set_style(card, "-webkit-backdrop-filter", f"blur({blur}px) saturate(110%)" if blur else "none")
    set_style(card, "box-shadow", "inset 1px 1px 0 rgba(255,255,255,0.28), inset 2px 2px 8px rgba(255,255,255,0.08), inset -1px -1px 4px rgba(0,0,0,0.14), 0 10px 26px rgba(0,0,0,0.22)"
              if th.get("shadow", True) else "inset 1px 1px 0 rgba(255,255,255,0.22)")
    txt = th.get("text_color") or "#FFFFFF"
    set_style(g["styles"]["name"], "color", txt)
    set_style(g["styles"]["name"], "font-size", f"{int(th.get('name_size', 20))}px")
    set_style(g["styles"]["label"], "color", rgba(txt, 0.82))
    set_style(g["styles"]["label"], "font-size", f"{int(th.get('label_size', 15))}px")
    set_style(g["styles"]["icon"], "color", txt)
    set_style(g["styles"]["icon"], "width", f"{int(th.get('icon_size', 34))}%")
    on_c, on_a, on_txt = th.get("tile_on_color") or "#FFFFFF", float(th.get("tile_on_opacity", 0.62)), th.get("text_on_color") or "#1C1C1E"
    for st in g.get("state", []):
        if st.get("operator") == "template":
            st["value"] = "[[[ return !!entity && " + json.dumps(ON_STATES).replace('"', "'") + ".includes(entity.state) ]]]"
            st["styles"] = {
                "card": [{"border": f"0.5px solid {rgba(on_c, 0.35)}"},
                         {"background": f"linear-gradient(135deg, {rgba(on_c, on_a)} 0%, {rgba(on_c, on_a * 0.76)} 55%, {rgba(on_c, on_a * 0.66)} 100%)"}],
                "icon": [{"color": on_txt}], "name": [{"color": on_txt}], "label": [{"color": rgba(on_txt, 0.75)}],
            }
    g["hold_action"] = {"action": beh.get("hold_action", "more-info")}
    on_state = next((st for st in g.get("state", []) if st.get("operator") == "template"), None)
    if on_state:
        tpl["hv_group_tile"]["state"] = [{"operator": "template", "value": GROUP_ANY_ON, "styles": copy.deepcopy(on_state["styles"])}]
    if "hw_fan_tile" in tpl:
        set_style(tpl["hw_fan_tile"]["styles"]["icon"], "color", txt)
        set_style(tpl["hw_fan_tile"]["styles"]["icon"], "width", f"{int(th.get('icon_size', 34))}%")

    # ---------- backgrounds ----------
    bg = th.get("background") or BASE_BG
    for v in d["views"]:
        if isinstance(v.get("background"), dict) and v["background"].get("image"):
            v["background"]["image"] = bg
            v["background"]["opacity"] = int(th.get("background_opacity", 100))

    # ---------- HOME board ----------
    home = find_view(d, "home")
    stack = home["cards"][0]["cards"]
    board = stack[0]
    base_cam = board["custom_fields"]["cam"]["card"]
    cols = max(1, int(L["grid"].get("columns", 5)))
    tiles = [t for t in L["tiles"] if 0 <= int(t.get("x", 0)) < cols]
    rows = max([int(t["y"]) + int(t.get("h", 1)) for t in tiles] + [1])
    cells = [["." for _ in range(cols)] for _ in range(rows)]
    cf, cf_styles = {}, {}
    cal_popup = next((c for c in stack if c.get("hash") == "#calendar"), None)
    popups = []
    stretch = [{"align-self": "stretch"}, {"justify-self": "stretch"}, {"min-width": "0"}]
    for i, t in enumerate(tiles):
        key = f"t{i}"
        x, y = int(t["x"]), int(t["y"])
        w, h = max(1, int(t.get("w", 1))), max(1, int(t.get("h", 1)))
        w = min(w, cols - x)
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                if cells[yy][xx] == ".":
                    cells[yy][xx] = key
        if t.get("kind") == "group":
            t = dict(t, _hash=f"#gruppo-{t.get('gid') or i + 1}")
            popups.append(group_popup(t, cal_popup, beh, info))
        c = build_tile(t, base_cam, src.get("camera") or BASE_CAMERA, beh, info)
        if t.get("kind") != "weather" and (w, h) != (1, 1):
            c.setdefault("styles", {}).setdefault("card", []).extend([{"aspect-ratio": "auto"}, {"height": "100%"}, {"box-sizing": "border-box"}])
        cf[key] = {"card": c}
        cf_styles[key] = copy.deepcopy(stretch)
    area_rows = [" ".join(r) for r in cells]
    if L["grid"].get("calendar_bar", True):
        cf["cal"] = {"card": {"type": "custom:button-card", "template": "hw_cal_bar"}}
        cf_styles["cal"] = copy.deepcopy(stretch)
        area_rows.append(" ".join(["cal"] * cols))
    stack[:] = [c for c in stack if not str(c.get("hash", "")).startswith("#gruppo-")] + [p for p in popups if p]
    board["custom_fields"] = cf
    board["styles"]["custom_fields"] = cf_styles
    board["styles"]["grid"] = [
        {"grid-template-areas": " ".join(f'"{r}"' for r in area_rows)},
        {"grid-template-columns": f"repeat({cols}, minmax(0, 1fr))"},
        {"grid-template-rows": " ".join(["auto"] * len(area_rows))},
        {"gap": f"{int(th.get('gap', 16))}px"},
    ]
    set_style(board["styles"]["card"], "max-width", f"{int(th.get('max_width', 1400))}px")

    # ---------- clocks ----------
    acc = th.get("accent") or BASE_ACCENT
    ch = th.get("clock_home", "original")
    if ch != "original":
        tpl["hw_clock"]["custom_fields"]["clock"] = clock_js(ch, acc, th.get("text_color") or "#FFFFFF")
        tpl["hw_clock"]["update_timer"] = 5000
    cw = th.get("clock_widgets", "original")
    if cw != "original" and "clock" in tpl.get("hw_widgets", {}).get("custom_fields", {}):
        tpl["hw_widgets"]["custom_fields"]["clock"] = clock_js(cw, "#E8590C", "#0B0B0C")
    cs = th.get("clock_screensaver", "original")
    wcards = d.get("wallpanel", {}).get("cards") or []
    faces = [f for f in (beh.get("faces") or ["clock"]) if f in FACE_IDS] or ["clock"]
    simple = faces == ["clock"] and not beh.get("night_mode")
    if wcards and "c" in wcards[0].get("custom_fields", {}):
        if simple and cs != "original":
            wcards[0]["custom_fields"]["c"] = clock_js(cs, acc, th.get("screensaver_text") or "#0B0B0C", SCREEN_W, True)
            wcards[0]["update_timer"] = 10000
        elif not simple:
            cfg = {
                "faces": faces, "interval": int(beh.get("face_interval", 60)),
                "clockStyle": "bold" if cs == "original" else cs, "accent": acc, "fg": th.get("screensaver_text") or "#0B0B0C",
                "lang": lang if lang in ("it", "en") else (L.get("language") if L.get("language") in ("it", "en") else "it"),
                "photos": [u for u in (wallpapers or []) if not u.split("?")[0].endswith("-dark.jpg")][:60],
                "photoDir": PHOTO_DIR if beh.get("photo_folder", True) else "", "photoInterval": int(beh.get("photo_interval", 20)),
                "motion": beh.get("motion_entity") or "", "weather": src.get("weather"),
                "cals": {c["entity"]: c.get("color") or "#FF9F0A" for c in cals},
                "night": {"on": bool(beh.get("night_mode")), "start": beh.get("night_start", "22:30"),
                          "end": beh.get("night_end", "07:00"), "dim": float(beh.get("night_dim", 0.35))},
            }
            wcards[0]["custom_fields"]["c"] = faces_js(cfg)
            wcards[0]["update_timer"] = 5000

    # ---------- light/dark wallpaper following the sun ----------
    dark = th.get("background_dark")
    if dark:
        board["triggers_update"] = "all"
        board["extra_styles"] = ("[[[ const night = states['sun.sun'] && states['sun.sun'].state === 'below_horizon';"
                                 f" const u = night ? {json.dumps(dark)} : {json.dumps(bg)};"
                                 " return `ha-card::before{content:'';position:fixed;inset:0;z-index:-1;pointer-events:none;"
                                 "background:url(\"${u}\") center / cover no-repeat;}`; ]]]")

    # ---------- cameras view ----------
    cams = [c for c in (src.get("cameras") or []) if c] or [src.get("camera") or BASE_CAMERA]
    build_cameras(d, cams, info)

    # ---------- behaviour ----------
    wp = d.setdefault("wallpanel", {})
    wp["enabled"] = bool(beh.get("screensaver", True))
    wp["idle_time"] = int(beh.get("idle_time", 120))
    for k in ("fullscreen", "hide_toolbar", "hide_sidebar"):
        wp[k] = bool(beh.get(k, False))
    sn = d.setdefault("swipe_nav", {})
    sn["enable_mouse_swipe"] = bool(beh.get("mouse_swipe", True))
    sn["animate"] = beh.get("swipe_animation", "swipe")
    sn["wrap"] = bool(beh.get("swipe_wrap", True))
    if beh.get("kiosk_always"):
        d["kiosk_mode"] = {"kiosk": True}
    else:
        d.pop("kiosk_mode", None)
    if not beh.get("show_widgets", True):
        d["views"] = [v for v in d["views"] if v.get("path") != "widgets"]
    if not beh.get("show_cameras", True):
        d["views"] = [v for v in d["views"] if v.get("path") != "cameras"]

    d["title"] = dash.get("title") or "Home View"
    lang = lang or L.get("language", "it")
    if lang == "en":
        d = to_english(d)
    return d


if __name__ == "__main__":
    import sys
    base = json.load(open(sys.argv[1]))
    lay = json.load(open(sys.argv[2])) if len(sys.argv) > 2 and sys.argv[2] != "-" else None
    json.dump(generate(base, lay), sys.stdout, ensure_ascii=False, indent=1)
