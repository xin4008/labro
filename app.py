import json
import os
import webbrowser
from datetime import datetime
from threading import Timer

from flask import Flask, request, jsonify, render_template, send_file, send_from_directory

from services.storage import (
    list_experiments,
    get_experiment,
    create_experiment,
    update_experiment,
    delete_experiment,
    save_photo,
    DATA_DIR,
)
from services.ai_service import generate_steps
from services.export import export_to_docx

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10MB

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# ─── Page Routes ────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/experiment/<exp_id>")
def workspace(exp_id):
    exp = get_experiment(exp_id)
    if not exp:
        return "实验不存在", 404
    return render_template("workspace.html", experiment=exp)


# ─── Static Data Files ─────────────────────────────────

@app.route("/data/<path:filepath>")
def serve_data_file(filepath):
    return send_from_directory(DATA_DIR, filepath)


# ─── Experiment CRUD API ───────────────────────────────

@app.route("/api/experiments", methods=["GET"])
def api_list_experiments():
    return jsonify(list_experiments())


@app.route("/api/experiments", methods=["POST"])
def api_create_experiment():
    data = request.get_json()
    exp = create_experiment(
        title=data.get("title", "未命名实验"),
        objective=data.get("objective", ""),
        references=data.get("references", ""),
    )
    return jsonify(exp), 201


@app.route("/api/experiments/<exp_id>", methods=["GET"])
def api_get_experiment(exp_id):
    exp = get_experiment(exp_id)
    if not exp:
        return jsonify({"error": "实验不存在"}), 404
    return jsonify(exp)


@app.route("/api/experiments/<exp_id>", methods=["PUT"])
def api_update_experiment(exp_id):
    data = request.get_json()
    data["updated_at"] = datetime.now().isoformat()
    update_experiment(exp_id, data)
    return jsonify({"ok": True})


@app.route("/api/experiments/<exp_id>", methods=["DELETE"])
def api_delete_experiment(exp_id):
    delete_experiment(exp_id)
    return jsonify({"ok": True})


# ─── Experiment Directory Info ─────────────────────────

@app.route("/api/experiments/<exp_id>/dir", methods=["GET"])
def api_get_experiment_dir(exp_id):
    from services.storage import _find_experiment_dir
    exp_dir = _find_experiment_dir(exp_id)
    if not exp_dir:
        return jsonify({"error": "not found"}), 404
    return jsonify({"dir_name": os.path.basename(exp_dir)})


# ─── AI Generation ─────────────────────────────────────

@app.route("/api/generate-steps", methods=["POST"])
def api_generate_steps():
    data = request.get_json()
    objective = data.get("objective", "")
    references = data.get("references", "")

    if not objective:
        return jsonify({"error": "请填写实验目的"}), 400

    try:
        steps = generate_steps(objective, references)
        return jsonify({"steps": steps})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"AI 生成失败：{str(e)}"}), 500


# ─── Photo Upload ──────────────────────────────────────

@app.route("/api/experiments/<exp_id>/upload-photo/<int:step_id>", methods=["POST"])
def api_upload_photo(exp_id, step_id):
    if "photo" not in request.files:
        return jsonify({"error": "未选择文件"}), 400

    file = request.files["photo"]
    if file.filename == "":
        return jsonify({"error": "未选择文件"}), 400

    allowed = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed:
        return jsonify({"error": f"不支持的图片格式：{ext}"}), 400

    try:
        rel_path = save_photo(exp_id, step_id, file)
        return jsonify({"path": rel_path})
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404


# ─── Export ────────────────────────────────────────────

@app.route("/api/experiments/<exp_id>/export-word", methods=["GET"])
def api_export_word(exp_id):
    exp = get_experiment(exp_id)
    if not exp:
        return jsonify({"error": "实验不存在"}), 404
    try:
        filepath = export_to_docx(exp)
        return send_file(filepath, as_attachment=True, download_name=os.path.basename(filepath))
    except Exception as e:
        return jsonify({"error": f"导出失败：{str(e)}"}), 500


# ─── Config API ────────────────────────────────────────

@app.route("/api/config", methods=["GET"])
def api_get_config():
    config = load_config()
    return jsonify({
        "deepseek_api_key": config.get("deepseek_api_key", ""),
        "deepseek_model": config.get("deepseek_model", "deepseek-chat"),
    })


@app.route("/api/config", methods=["PUT"])
def api_update_config():
    data = request.get_json()
    config = load_config()
    if "deepseek_api_key" in data:
        config["deepseek_api_key"] = data["deepseek_api_key"]
    if "deepseek_model" in data:
        config["deepseek_model"] = data["deepseek_model"]
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    return jsonify({"ok": True})


# ─── Startup ───────────────────────────────────────────

def open_browser():
    config = load_config()
    host = config.get("host", "127.0.0.1")
    port = config.get("port", 5000)
    webbrowser.open(f"http://{host}:{port}")


if __name__ == "__main__":
    config = load_config()
    host = config.get("host", "127.0.0.1")
    port = config.get("port", 5000)
    Timer(1.5, open_browser).start()
    print(f"\n  化学实验助手已启动 -> http://{host}:{port}\n")
    app.run(host=host, port=port, debug=False)
