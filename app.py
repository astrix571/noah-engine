from flask import jsonify
import os, json, logging

LOG = logging.getLogger(__name__)

DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "memory.json")

def _safe_load():
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        if not os.path.exists(DATA_FILE):
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump([], f)
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            data = []
        return data
    except Exception as e:
        LOG.exception("Failed to load memory.json")
        return []

@app.route("/memory/list", methods=["GET"])
def memory_list():
    try:
        data = _safe_load()
        return jsonify({"status": "ok", "data": data}), 200
    except Exception as e:
        LOG.exception("memory_list failed")
        return jsonify({"status": "error", "error": str(e)}), 500
