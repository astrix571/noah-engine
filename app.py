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

# === Helpers (memory) ===
def _load_mem() -> dict:
    if not MEM_PATH.exists():
        return {}
    try:
        return json.loads(MEM_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}

def _save_mem(d: dict) -> None:
    MEM_PATH.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")

# === UI ===
@app.route("/")
def home():
    return render_template("index.html")

# Privacy Policy (serves ./static/privacy.html)
@app.route("/privacy")
def privacy():
    return app.send_static_file("privacy.html")

# === Noah Memory API ===
@app.route("/memory/list", methods=["GET"])
def list_memory():
    mem = _load_mem()
    data = [{"key": k, "value": v} for k, v in mem.items()]
    return jsonify({"status": "ok", "data": data})

@app.route("/memory/add", methods=["POST"])
def add_memory():
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
    key = request.args.get("key", "")
    if not key:
        return jsonify({"status": "error", "error": "missing key"}), 400
    mem = _load_mem()
    if key not in mem:
        return jsonify({"status": "error", "error": "not found"}), 404
    return jsonify({"status": "ok", "data": {"key": key, "value": mem[key]}})

@app.route("/memory/delete", methods=["DELETE"])
def delete_memory():
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

# === Chat ===
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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
