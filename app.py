import os

from flask import Flask, jsonify, send_from_directory

from backend.account import account_bp
from backend.auth import auth_bp
from backend.chat import chat_bp
from backend.privacy import privacy_bp
from backend.db import init_db

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(BASE_DIR, "dist")

app = Flask(__name__, static_folder=None)
app.config["MAX_CONTENT_LENGTH"] = 1_100_000
app.register_blueprint(auth_bp)
app.register_blueprint(account_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(privacy_bp)

_initialized = False


def ensure_db():
    global _initialized
    if not _initialized:
        init_db()
        _initialized = True


@app.before_request
def before_request():
    if os.getenv("DATABASE_URL"):
        ensure_db()


@app.get("/api/health")
def health():
    return jsonify({"ok": True, "backend": "Flask", "database": "PostgreSQL"})


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def static_app(path):
    if path.startswith("api/"):
        return jsonify({"error": "Recurso não encontrado."}), 404
    if path:
        target = os.path.join(DIST_DIR, path)
        if os.path.isfile(target):
            return send_from_directory(DIST_DIR, path)
    return send_from_directory(DIST_DIR, "index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=os.getenv("FLASK_DEBUG") == "1")
