from flask import Flask, request, render_template
import json
import os
import yaml

app = Flask(__name__)
MEMORY_FILE = 'memory.json'

def load_identity():
    with open("identity.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)

@app.route("/", methods=["GET", "POST"])
def chat():
    memory = load_memory()
    identity = load_identity()

    if request.method == "POST":
        user_input = request.form["user_input"]
        memory.append({"user": user_input})
        response = f"{identity['name']}: אני כאן בשבילך. אמרת: {user_input}"
        memory.append({"noah": response})
        save_memory(memory)

    return render_template("index.html", memory=memory)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
