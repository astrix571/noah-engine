from flask import Flask, jsonify, request, send_from_directory
import os, json, logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger("noah-memory")

# ---------- Storage helpers ----------
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
DATA_FILE = os.path.join(DATA_DIR, "memory.json")

def ensure_store():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)

def load_store():
    ensure_store()
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            return data if isinstance(data, list) else []
        except Exception:
            return []

def save_store(items):
    ensure_store()
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

# ---------- Routes ----------
@app.route("/")
def home():
    return "Noah Engine is up", 200

@app.route("/privacy")
def privacy():
    return "Noah Engine Privacy Policy: We store key/value memory pairs server-side in a local JSON file. No personal data is shared.", 200

@app.route("/memory/list", methods=["GET"])
def memory_list():
    # בדיקה: מחזיר תוכן קבוע. אם זה עובד – הבעיה באחסון/קובץ.
    from flask import jsonify
    return jsonify({"status": "ok", "data": []}), 200

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
        found = False
        for item in data:
            if item.get("key") == key:
                item["value"] = value
                found = True
                break
        if not found:
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

# Render expects app to run via gunicorn; no need for app.run() here.
