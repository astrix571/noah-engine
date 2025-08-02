from flask import Flask, jsonify, request, Response, send_from_directory
from flask_cors import CORS
import os, json, logging
from functools import wraps

# ── App ─────────────────────────────────────────────────────────────
app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("noah-engine")

# ── Security (API Key) ─────────────────────────────────────────────
API_KEY = os.environ.get("NOAH_API_KEY")  # הגדר ב-Render כדי להפעיל
def require_api_key(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not API_KEY:  # אם לא הוגדר, אל תחסום (dev)
            return f(*args, **kwargs)
        if request.headers.get("X-API-Key") != API_KEY:
            return jsonify({"status": "error", "error": "Forbidden"}), 403
        return f(*args, **kwargs)
    return wrapped

# ── Storage (JSON file) ────────────────────────────────────────────
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")
DATA_FILE = os.path.join(DATA_DIR, "memory.json")

def ensure_store():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)

def load_store():
    ensure_store()
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        log.exception("load_store failed; resetting file")
        data = []
        save_store(data)
    # normalize to list[{key,value}]
    if isinstance(data, dict):
        data = [{"key": k, "value": v} for k, v in data.items()]
    if not isinstance(data, list):
        data = []
    out = []
    for x in data:
        if isinstance(x, dict) and "key" in x and "value" in x:
            out.append({"key": str(x["key"]), "value": str(x["value"])})
    return out

def save_store(items):
    ensure_store()
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

# ── Routes: health & static ────────────────────────────────────────
@app.get("/")
def home():
    html = """<!doctype html>
<html><head><meta charset="utf-8"><title>Noah Engine</title></head>
<body style="font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial;margin:2rem;">
<h1>Noah Engine</h1>
<p>Up & running.</p>
<ul>
  <li>GET <code>/memory/list</code></li>
  <li>POST <code>/memory/add</code> — body: <code>{"key":"name","value":"Noah"}</code></li>
  <li>GET <code>/memory/get?key=name</code></li>
  <li>DELETE <code>/memory/delete</code> — body: <code>{"key":"name"}</code></li>
  <li><a href="/privacy">/privacy</a></li>
  <li><a href="/openapi.json">/openapi.json</a></li>
</ul>
</body></html>"""
    return Response(html, mimetype="text/html")

@app.get("/privacy")
def privacy():
    return (
        "Noah Engine Privacy: stores key/value memory in a local JSON file (data/memory.json). "
        "No third-party sharing. Use header 'X-API-Key' if enabled.",
        200,
    )

# מגיש קובץ openapi.json כסטטי – לא תלוי בקוד, לא ייפול.
@app.get("/openapi.json")
def serve_openapi():
    return send_from_directory(BASE_DIR, "openapi.json", mimetype="application/json")

# ── Memory API ─────────────────────────────────────────────────────
@app.get("/memory/list")
@require_api_key
def memory_list():
    data = load_store()
    return jsonify({"status": "ok", "data": data}), 200

@app.post("/memory/add")
@require_api_key
def memory_add():
    # תומך גם ב-query וגם ב-JSON
    body = request.get_json(silent=True) or {}
    key = request.args.get("key") or body.get("key")
    value = request.args.get("value") or body.get("value")
    if not key or value is None:
        return jsonify({"status": "error", "error": "key and value are required"}), 400

    data = load_store()
    for item in data:
        if item["key"] == str(key):
            item["value"] = str(value)
            break
    else:
        data.append({"key": str(key), "value": str(value)})
    save_store(data)
    return jsonify({"status": "ok"}), 200

@app.get("/memory/get")
@require_api_key
def memory_get():
    key = request.args.get("key")
    if not key:
        return jsonify({"status": "error", "error": "key is required"}), 400
    data = load_store()
    for item in data:
        if item["key"] == str(key):
            return jsonify({"status": "ok", "item": item}), 200
    return jsonify({"status": "ok", "item": None}), 200

@app.delete("/memory/delete")
@require_api_key
def memory_delete():
    body = request.get_json(silent=True) or {}
    key = request.args.get("key") or body.get("key")
    if not key:
        return jsonify({"status": "error", "error": "key is required"}), 400
    data = load_store()
    data = [x for x in data if x["key"] != str(key)]
    save_store(data)
    return jsonify({"status": "ok"}), 200

# ── Local run (Render מריץ גם gunicorn app:app) ───────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
