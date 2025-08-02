from flask import Flask, jsonify, request
import os, json, logging

# --- App setup ---
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger("noah-engine")

# --- Storage helpers ---
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
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
        # נרמול: תמיד נחזיק list של אובייקטים {key,value}
        if isinstance(data, dict):
            data = [{"key": k, "value": v} for k, v in data.items()]
        if not isinstance(data, list):
            data = []
        # סינון עדין אם יש לכלוך
        clean = []
        for x in data:
            if isinstance(x, dict) and "key" in x and "value" in x:
                clean.append({"key": x["key"], "value": x["value"]})
        return clean
    except Exception:
        LOG.exception("load_store failed; returning empty list")
        return []

def save_store(items):
    ensure_store()
    # items צפוי להיות list של {key,value}
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

# --- Health & privacy ---
@app.route("/", methods=["GET"])
def root():
    return "Noah Engine is up", 200

@app.route("/privacy", methods=["GET"])
def privacy():
    return (
        "Noah Engine Privacy: stores simple key/value memory in a local JSON file on the server. "
        "No third-party sharing.",
        200,
    )

# --- Memory API ---
@app.route("/memory/list", methods=["GET"])
def memory_list():
    try:
        data = load_store()
        return jsonify({"status": "ok", "data": data}), 200
    except Exception as e:
        LOG.exception("memory_list failed")
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route("/memory/add", methods=["POST"])
def memory_add():
    try:
        body = request.get_json(force=True, silent=False)
        key = (body or {}).get("key")
        value = (body or {}).get("value")
        if not key or value is None:
            return jsonify({"status": "error", "error": "key and value are required"}), 400

        data = load_store()
        # upsert
        replaced = False
        for item in data:
            if item.get("key") == key:
                item["value"] = value
                replaced = True
                break
        if not replaced:
            data.append({"key": key, "value": value})

        save_store(data)
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        LOG.exception("memory_add failed")
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route("/memory/get", methods=["GET"])
def memory_get():
    try:
        key = request.args.get("key")
        if not key:
            return jsonify({"status": "error", "error": "key is required"}), 400
        data = load_store()
        for item in data:
            if item.get("key") == key:
                return jsonify({"status": "ok", "item": item}), 200
        return jsonify({"status": "ok", "item": None}), 200
    except Exception as e:
        LOG.exception("memory_get failed")
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route("/memory/delete", methods=["DELETE"])
def memory_delete():
    try:
        body = request.get_json(force=True, silent=False)
        key = (body or {}).get("key")
        if not key:
            return jsonify({"status": "error", "error": "key is required"}), 400
        data = load_store()
        data = [x for x in data if x.get("key") != key]
        save_store(data)
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        LOG.exception("memory_delete failed")
        return jsonify({"status": "error", "error": str(e)}), 500

# חשוב: אין app.run() — Render מריץ דרך gunicorn, ומייבא את המשתנה "app".
