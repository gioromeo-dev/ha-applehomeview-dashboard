"""Home View Studio — Home Assistant add-on backend (stdlib only, served through Ingress)."""
import base64
import json
import os
import re
import shutil
import socket
import struct
import sys
import time
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, os.path.dirname(__file__))
import generator  # noqa: E402

APP = os.path.dirname(os.path.abspath(__file__))
DATA = "/data"
LAYOUT_FILE = os.path.join(DATA, "layout.json")
BACKUPS = os.path.join(DATA, "backups")
HA_CONFIG = "/homeassistant" if os.path.isdir("/homeassistant") else "/config"
BG_DIR = os.path.join(HA_CONFIG, "www", "homeview")
TOKEN = os.environ.get("SUPERVISOR_TOKEN", "")
PORT = int(os.environ.get("INGRESS_PORT", "8099"))
IMG_EXT = (".jpg", ".jpeg", ".png", ".webp", ".gif")


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


# ---------------------------------------------------------------- websocket to Core
class CoreWS:
    def __init__(self):
        self.s = socket.create_connection(("supervisor", 80), timeout=60)
        key = base64.b64encode(os.urandom(16)).decode()
        self.s.sendall((f"GET /core/websocket HTTP/1.1\r\nHost: supervisor\r\nUpgrade: websocket\r\n"
                        f"Connection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n").encode())
        self.buf = b""
        while b"\r\n\r\n" not in self.buf:
            chunk = self.s.recv(4096)
            if not chunk:
                raise ConnectionError("websocket handshake failed")
            self.buf += chunk
        head, self.buf = self.buf.split(b"\r\n\r\n", 1)
        if b" 101 " not in head.split(b"\r\n")[0]:
            raise ConnectionError(head.decode(errors="replace"))
        self.n = 0
        self.recv()  # auth_required
        self.send({"type": "auth", "access_token": TOKEN})
        r = self.recv()
        if r.get("type") != "auth_ok":
            raise PermissionError(str(r))

    def _recvn(self, n):
        while len(self.buf) < n:
            chunk = self.s.recv(1 << 16)
            if not chunk:
                raise EOFError
            self.buf += chunk
        out, self.buf = self.buf[:n], self.buf[n:]
        return out

    def recv(self):
        data = b""
        while True:
            b1, b2 = self._recvn(2)
            ln = b2 & 0x7F
            if ln == 126:
                ln = struct.unpack(">H", self._recvn(2))[0]
            elif ln == 127:
                ln = struct.unpack(">Q", self._recvn(8))[0]
            payload = self._recvn(ln)
            op = b1 & 0x0F
            if op == 9:  # ping -> ignore
                continue
            data += payload
            if b1 & 0x80:
                return json.loads(data)

    def send(self, obj):
        p = json.dumps(obj).encode()
        mask = os.urandom(4)
        h = bytes([0x81])
        n = len(p)
        if n < 126:
            h += bytes([0x80 | n])
        elif n < 65536:
            h += bytes([0x80 | 126]) + struct.pack(">H", n)
        else:
            h += bytes([0x80 | 127]) + struct.pack(">Q", n)
        self.s.sendall(h + mask + bytes(c ^ mask[i % 4] for i, c in enumerate(p)))

    def call(self, msg_type, **kw):
        self.n += 1
        mid = self.n
        self.send({"id": mid, "type": msg_type, **kw})
        while True:
            r = self.recv()
            if r.get("id") == mid and r.get("type") == "result":
                if not r.get("success"):
                    raise RuntimeError((r.get("error") or {}).get("message", str(r)))
                return r.get("result")

    def close(self):
        try:
            self.s.close()
        except OSError:
            pass


def with_ws(fn):
    ws = CoreWS()
    try:
        return fn(ws)
    finally:
        ws.close()


# ---------------------------------------------------------------- data helpers
def load_layout():
    try:
        with open(LAYOUT_FILE, encoding="utf-8") as f:
            return generator.normalize(json.load(f))
    except (OSError, ValueError):
        return generator.normalize(None)


def save_layout(layout):
    os.makedirs(DATA, exist_ok=True)
    tmp = LAYOUT_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(layout, f, ensure_ascii=False, indent=1)
    os.replace(tmp, LAYOUT_FILE)


def load_base():
    with open(os.path.join(APP, "base.json"), encoding="utf-8") as f:
        return json.load(f)


def list_entities():
    def run(ws):
        states = ws.call("get_states")
        ents = {e["entity_id"]: e for e in ws.call("config/entity_registry/list")}
        devs = {d["id"]: d for d in ws.call("config/device_registry/list")}
        areas = {a["area_id"]: a["name"] for a in ws.call("config/area_registry/list")}
        return states, ents, devs, areas

    states, ents, devs, areas = with_ws(run)
    out = []
    for s in states:
        eid = s["entity_id"]
        a = s.get("attributes", {})
        reg = ents.get(eid) or {}
        area_id = reg.get("area_id") or (devs.get(reg.get("device_id")) or {}).get("area_id")
        out.append({
            "entity_id": eid,
            "domain": eid.split(".", 1)[0],
            "name": a.get("friendly_name") or eid,
            "state": s.get("state"),
            "icon": a.get("icon") or reg.get("icon") or reg.get("original_icon"),
            "unit": a.get("unit_of_measurement"),
            "device_class": a.get("device_class"),
            "picture": a.get("entity_picture"),
            "area": areas.get(area_id) if area_id else None,
            "hidden": bool(reg.get("hidden_by")) or bool(reg.get("entity_category")),
            "attrs": {k: a[k] for k in ("temperature", "current_temperature", "media_title", "current_position", "hvac_action") if k in a},
        })
    out.sort(key=lambda e: (e["domain"], e["name"].lower()))
    return out


BUNDLED = "studio"  # original wallpapers shipped with the add-on (MIT)


def install_bundled_wallpapers():
    src = os.path.join(APP, "wallpapers")
    dst = os.path.join(BG_DIR, BUNDLED)
    try:
        for root, _dirs, files in os.walk(src):
            out = os.path.join(dst, os.path.relpath(root, src))
            os.makedirs(out, exist_ok=True)
            for f in files:
                if not os.path.exists(os.path.join(out, f)):
                    shutil.copy2(os.path.join(root, f), os.path.join(out, f))
    except OSError as e:
        log("bundled wallpapers not installed:", e)


def list_backgrounds():
    """Images in /config/www/homeview (your uploads) and one level of sub-folders, grouped by folder."""
    out = []
    try:
        entries = sorted(os.listdir(BG_DIR))
    except OSError:
        entries = []
    folders = [""] + [d for d in entries if os.path.isdir(os.path.join(BG_DIR, d)) and not d.startswith(".")]
    folders.sort(key=lambda d: (d != BUNDLED, d != "", d))
    for d in folders:
        path = os.path.join(BG_DIR, d)
        try:
            files = sorted(f for f in os.listdir(path) if f.lower().endswith(IMG_EXT) and not f.startswith("."))
        except OSError:
            continue
        group = "Home View Studio" if d == BUNDLED else ("I tuoi sfondi" if d == "" else d.replace("_", " ").replace("-", " ").title())
        for f in files:
            stem = os.path.splitext(f)[0]
            rel = f"{d}/{f}" if d else f
            thumb = f"/local/homeview/{d}/thumbs/{f}" if d and os.path.exists(os.path.join(path, "thumbs", f)) else f"/local/homeview/{rel}"
            out.append({"name": stem, "url": f"/local/homeview/{rel}", "thumb": thumb, "group": group,
                        "variant": "dark" if stem.endswith("-dark") else "light" if stem.endswith("-light") else ""})
    return out


def apply_layout(layout, ui_lang=None):
    url = (layout.get("dashboard", {}).get("url_path") or "home-view").strip("/")
    title = layout.get("dashboard", {}).get("title") or "Home View"
    if not re.fullmatch(r"[a-z0-9]+-[a-z0-9-]+", url):
        raise ValueError("Il percorso della dashboard deve contenere un trattino, es. home-view")

    def run(ws):
        info = {s["entity_id"]: {"device_class": s.get("attributes", {}).get("device_class"),
                                 "icon": s.get("attributes", {}).get("icon"),
                                 "name": s.get("attributes", {}).get("friendly_name")} for s in ws.call("get_states")}
        lang = layout.get("language", "auto")
        if lang not in ("it", "en") and ui_lang in ("it", "en"):
            lang = ui_lang  # "auto": the language of the person using the editor
        if lang not in ("it", "en"):
            core_lang = (ws.call("get_config") or {}).get("language") or "en"
            lang = "it" if core_lang.startswith("it") else "en"
        cfg = generator.generate(load_base(), layout, info, lang, [b["url"] for b in list_backgrounds()])
        dash = ws.call("lovelace/dashboards/list")
        existing = next((d for d in dash if d.get("url_path") == url), None)
        if not existing:
            ws.call("lovelace/dashboards/create", url_path=url, title=title, icon="mdi:tablet-dashboard",
                    show_in_sidebar=True, require_admin=False, mode="storage")
        else:
            try:  # keep a backup of what we are about to overwrite
                old = ws.call("lovelace/config", url_path=url)
                os.makedirs(BACKUPS, exist_ok=True)
                fn = os.path.join(BACKUPS, f"{url}-{time.strftime('%Y%m%d-%H%M%S')}.json")
                with open(fn, "w", encoding="utf-8") as f:
                    json.dump(old, f, ensure_ascii=False)
                for old_fn in sorted(os.listdir(BACKUPS))[:-20]:
                    os.remove(os.path.join(BACKUPS, old_fn))
            except Exception as e:  # noqa: BLE001
                log("backup skipped:", e)
            if existing.get("title") != title:
                ws.call("lovelace/dashboards/update", dashboard_id=existing["id"], title=title)
        ws.call("lovelace/config/save", url_path=url, config=cfg)
        return {"url_path": url, "views": [v.get("path") for v in cfg["views"]]}

    return with_ws(run)


def list_backups():
    try:
        return sorted(os.listdir(BACKUPS), reverse=True)
    except OSError:
        return []


def restore_backup(name):
    if not re.fullmatch(r"[a-z0-9-]+-\d{8}-\d{6}\.json", name or ""):
        raise ValueError("backup non valido")
    with open(os.path.join(BACKUPS, name), encoding="utf-8") as f:
        cfg = json.load(f)
    url = name.rsplit("-", 2)[0]
    with_ws(lambda ws: ws.call("lovelace/config/save", url_path=url, config=cfg))
    return {"restored": name, "url_path": url}


# ---------------------------------------------------------------- HTTP
class Handler(BaseHTTPRequestHandler):
    server_version = "HomeViewStudio/1.0"

    def log_message(self, fmt, *args):
        if not self.path.startswith("/api/entities"):
            log(self.command, self.path.split("?")[0], fmt % args if "%" in fmt else "")

    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        if not isinstance(body, (bytes, bytearray)):
            body = json.dumps(body, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _body(self):
        n = int(self.headers.get("Content-Length") or 0)
        if n > 25 * 1024 * 1024:
            raise ValueError("file troppo grande (max 25 MB)")
        return self.rfile.read(n) if n else b""

    def _allowed(self):
        ip = self.client_address[0]
        if ip in ("172.30.32.2", "127.0.0.1", "::1"):
            return True
        self._send(403, {"error": "solo tramite Ingress"})
        return False

    def do_GET(self):
        if not self._allowed():
            return
        u = urlparse(self.path)
        p = u.path.rstrip("/") or "/"
        try:
            if p == "/":
                with open(os.path.join(APP, "www", "index.html"), "rb") as f:
                    return self._send(200, f.read(), "text/html; charset=utf-8")
            if p == "/api/entities":
                return self._send(200, list_entities())
            if p == "/api/layout":
                return self._send(200, load_layout())
            if p == "/api/default":
                return self._send(200, generator.normalize(None))
            if p == "/api/backgrounds":
                return self._send(200, list_backgrounds())
            if p == "/api/backups":
                return self._send(200, list_backups())
            if p == "/i18n.js":
                with open(os.path.join(APP, "www", "i18n.js"), "rb") as f:
                    return self._send(200, f.read(), "text/javascript; charset=utf-8")
            if p == "/api/faces.js":
                with open(os.path.join(APP, "faces.js"), "rb") as f:
                    return self._send(200, f.read(), "text/javascript; charset=utf-8")
            if p == "/api/clock.js":
                with open(os.path.join(APP, "clock.js"), "rb") as f:
                    return self._send(200, f.read(), "text/javascript; charset=utf-8")
            if p == "/api/meta":
                return self._send(200, {"styles": generator.STYLE_CHOICES})
            if p == "/api/preview":
                lang = (parse_qs(u.query).get("lang") or [None])[0]
                return self._send(200, generator.generate(load_base(), load_layout(), None, lang))
            return self._send(404, {"error": "not found"})
        except Exception as e:  # noqa: BLE001
            traceback.print_exc()
            return self._send(500, {"error": str(e)})

    def do_POST(self):
        if not self._allowed():
            return
        u = urlparse(self.path)
        p = u.path.rstrip("/")
        q = parse_qs(u.query)
        try:
            if p == "/api/layout":
                lay = generator.normalize(json.loads(self._body()))
                save_layout(lay)
                return self._send(200, {"ok": True})
            if p == "/api/apply":
                body = self._body()
                lay = generator.normalize(json.loads(body)) if body else load_layout()
                save_layout(lay)
                res = apply_layout(lay, (q.get("lang") or [None])[0])
                log("applied", res)
                return self._send(200, {"ok": True, **res})
            if p == "/api/backgrounds":
                name = os.path.basename((q.get("name") or ["sfondo.jpg"])[0])
                stem, ext = os.path.splitext(name)
                if ext.lower() not in IMG_EXT:
                    raise ValueError("formato non supportato (jpg, png, webp, gif)")
                stem = re.sub(r"[^A-Za-z0-9_-]+", "-", stem).strip("-")[:40] or "sfondo"
                data = self._body()
                if not data:
                    raise ValueError("file vuoto")
                os.makedirs(BG_DIR, exist_ok=True)
                fn = f"{stem}-{int(time.time())}{ext.lower()}"
                with open(os.path.join(BG_DIR, fn), "wb") as f:
                    f.write(data)
                return self._send(200, {"name": fn, "url": f"/local/homeview/{fn}"})
            if p == "/api/restore":
                return self._send(200, restore_backup(json.loads(self._body()).get("name")))
            return self._send(404, {"error": "not found"})
        except Exception as e:  # noqa: BLE001
            traceback.print_exc()
            return self._send(400, {"error": str(e)})


def import_layout_file():
    """/config/homeview_studio/import.json -> merged into the saved layout (optionally published), then renamed."""
    path = os.path.join(HA_CONFIG, "homeview_studio", "import.json")
    if not os.path.exists(path):
        return
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        opts = {k: data.pop(k) for k in list(data) if k.startswith("_")}
        lay = load_layout() if opts.get("_merge", True) else generator.normalize(None)
        lay.update(data)
        lay = generator.normalize(lay)
        save_layout(lay)
        log("layout imported from", path)
        if opts.get("_apply"):
            log("applied", apply_layout(lay, opts.get("_lang")))
        os.replace(path, path + time.strftime(".done-%Y%m%d-%H%M%S"))
    except Exception as e:  # noqa: BLE001
        log("layout import failed:", e)
        traceback.print_exc()


if __name__ == "__main__":
    log(f"Home View Studio on :{PORT} (config dir {HA_CONFIG})")
    install_bundled_wallpapers()
    import_layout_file()
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
