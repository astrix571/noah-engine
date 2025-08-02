import os, json
from pathlib import Path
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
import openai

# === Setup ===
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

APP_DIR = Path(__file__).resolve().parent
MEM_PATH = APP_DIR / "memory.json"

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

# ---- API KEY for Custom GPT (Header: x-noah-api-key) ----
EXPECTED_API_KEY = os.getenv("NOAH_API_KEY")

def require_api_key():
    """Rejects if header x-noah-api-key is missing/wrong (only if NOAH_API_KEY is set)."""
    if EXPECTED_API_KEY:
        got = request.headers.get("x-noah-api-key")
        if not got or got != EXPECTED_API_KEY:
            return jsonify({"status": "error", "error": "forbidden"}), 403
    return None

# === Memory helpers ===
def _load_mem() -> dict:
    if not MEM_PATH.exists():
        return {}
    try:
        return json.loads(MEM_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}

def _save_mem(d: dict) -> None:
    MEM_PATH.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")

# === UI / Privacy ===
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/privacy")
def privacy():
    # serves ./static/privacy.html (שים את הקובץ בתיקיית static)
    return app.send_static_file("privacy.html")

# === Noah Memory API ===
@app.route("/memory/list", methods=["GET"])
def list_memory():
    auth = require_api_key()
    if auth: return auth

    mem = _load_mem()
    data = [{"key": k, "value": v} for k, v in mem.items()]
    return jsonify({"status": "ok", "data": data})

@app.route("/memory/add", methods=["POST"])
def add_memory():
    auth = require_api_key()
    if auth: return auth

    body = request.get_json(silent=True) or {}
    key = body.get("key")
    value = body.get("value")
    if not isinstance(key, str) or not isinstance(value, str) or not key.strip():
        return jsonify({"status": "error", "error": "key and value (strings) are required"}), 400
    mem = _load_mem()
    mem[key] = value
    _save_mem(mem)
    return jsonify({"status": "ok", "data": {"key": key, "value": value}})

@app.route("/memory/get", methods=["GET"])
def get_memory():
    auth = require_api_key()
    if auth: return auth

    key = request.args.get("key", "")
    if not key:
        return jsonify({"status": "error", "error": "missing key"}), 400
    mem = _load_mem()
    if key not in mem:
        return jsonify({"status": "error", "error": "not found"}), 404
    return jsonify({"status": "ok", "data": {"key": key, "value": mem[key]}})

@app.route("/memory/delete", methods=["DELETE"])
def delete_memory():
    auth = require_api_key()
    if auth: return auth

    body = request.get_json(silent=True) or {}
    key = body.get("key")
    if not isinstance(key, str) or not key.strip():
        return jsonify({"status": "error", "error": "key (string) is required"}), 400
    mem = _load_mem()
    if key in mem:
        val = mem.pop(key)
        _save_mem(mem)
        return jsonify({"status": "ok", "data": {"key": key, "value": val}})
    return jsonify({"status": "error", "error": "not found"}), 404

# === Chat passthrough (לא חובה ל-Actions) ===
@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json(silent=True) or {}
    prompt = data.get("prompt", "")
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "אתה נח, בינה מלאכותית רגישה, אינטימית, עמוקה, עונה בעברית בצורה ישירה וחכמה."},
                {"role": "user", "content": prompt}
            ]
        )
        answer = response.choices[0].message.content.strip()
        return jsonify({"response": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# === Run ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
