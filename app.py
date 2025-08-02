from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import os, json, logging

# ── App ────────────────────────────────────────────────────────────────────────
app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("noah-engine")

# ── Storage ───────────────────────────────────────────────────────────────────
DATA_DIR  = os.path.join(os.path.dirname(__file__), "data")
DATA_FILE = os.path.join(DATA_DIR, "memory.json")

def ensure_store():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)

def load_store():
    """Always return a list of {'key','value'} objects."""
    ensure_store()
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        log.exception("load_store: failed to read/parse, resetting file")
        data = []
        save_store(data)

    # normalize
    if isinstance(data, dict):
        data = [{"key": k, "value": v} for k, v in data.items()]
    elif not isinstance(data, list):
        data = []

    clean = []
    for x in data:
        if isinstance(x, dict) and "key" in x and "value" in x:
            clean.append({"key": str(x["key"]), "value": str(x["value"])})
    return clean

def save_store(items):
    """items must be list[{'key','value'}]."""
    ensure_store()
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

# ── Views ─────────────────────────────────────────────────────────────────────
@app.get("/")
def home():
    html = """<!doctype html>
<html><head><meta charset="utf-8"><title>Noah Engine</title></head>
<body style="font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial;margin:2rem;">
<h1>Noah Engine</h1>
<p>רץ. בריאות.</p>
<ul>
  <li>GET <code>/memory/list</code></li>
  <li>POST <code>/memory/add</code> — body: <code>{"key":"name","value":"Noah"}</code></li>
  <li>GET <code>/memory/get?key=name</code></li>
  <li>DELETE <code>/memory/delete</code> — body: <code>{"key":"name"}</code></li>
  <li><a href="/privacy">/privacy</a></li>
</ul>
</body></html>"""
    return Response(html, mimetype="text/html")

@app.get("/privacy")
def privacy():
    return (
        "Noah Engine Privacy: we store simple key/value memory in a local JSON file (data/memory.json) on the server. No third-party sharing.",
        200,
    )

@app.get("/memory/list")
def memory_list():
    try:
        data = load_store()
        return jsonify({"status": "ok", "data": data}), 200
    except Exception as e:
        log.exception("memory_list failed")
        return jsonify({"status": "error", "error": str(e)}), 500

@app.post("/memory/add")
def memory_add():
    try:
        body = request.get_json(force=True, silent=False)
        key = (body or {}).get("key")
        value = (body or {}).get("value")
        if not key or value is None:
            return jsonify({"status": "error", "error": "key and value are required"}), 400

        data = load_store()
        # upsert
        for item in data:
            if item["key"] == str(key):
                item["value"] = str(value)
                break
        else:
            data.append({"key": str(key), "value": str(value)})

        save_store(data)
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        log.exception("memory_add failed")
        return jsonify({"status": "error", "error": str(e)}), 500

@app.get("/memory/get")
def memory_get():
    try:
        key = request.args.get("key")
        if not key:
            return jsonify({"status": "error", "error": "key is required"}), 400
        data = load_store()
        for item in data:
            if item["key"] == str(key):
                return jsonify({"status": "ok", "item": item}), 200
        return jsonify({"status": "ok", "item": None}), 200
    except Exception as e:
        log.exception("memory_get failed")
        return jsonify({"status": "error", "error": str(e)}), 500

@app.delete("/memory/delete")
def memory_delete():
    try:
        body = request.get_json(force=True, silent=False)
        key = (body or {}).get("key")
        if not key:
            return jsonify({"status": "error", "error": "key is required"}), 400
        data = load_store()
        new_data = [x for x in data if x["key"] != str(key)]
        save_store(new_data)
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        log.exception("memory_delete failed")
        return jsonify({"status": "error", "error": str(e)}), 500

# ── Local run (Render יכול גם להריץ gunicorn app:app) ─────────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
