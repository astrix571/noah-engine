@app.route("/memory/list", methods=["GET"])
def list_memory():
    try:
        # הנחה: יש לך קריאה קיימת שטוענת את הזיכרון לקובץ/RAM.
        # אם אצלך השם שונה (load_store / read_mem וכו׳) השאר אותו.
        mem = load_store()  # <-- אם אצלך זה פונקציה בשם אחר, השאר את השם המקורי.

        # נרמול: תומך גם ב-dict וגם ב-list
        if isinstance(mem, dict):
            data = [{"key": k, "value": v} for k, v in mem.items()]
        elif isinstance(mem, list):
            # אם זה כבר פורמט [{key,value}] נשאיר; אחרת נסנן למה שיש.
            data = [
                {"key": x.get("key", ""), "value": x.get("value", "")}
                for x in mem
                if isinstance(x, dict)
            ]
        else:
            data = []

        return jsonify({"status": "ok", "data": data}), 200
    except Exception as e:
        app.logger.exception("list_memory failed")
        return jsonify({"status": "error", "error": str(e)}), 500
