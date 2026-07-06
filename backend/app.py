"""
Study Time - Plataforma auxiliar para estudos ENEM
Aplicação Flask (backend) — arquitetura cliente-servidor (RS01, RS03).

Executa a API REST e também serve o frontend estático (HTML/CSS/JS),
permitindo rodar toda a plataforma com um único comando.
"""
import os

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

from config import Config
from models import db

FRONTEND_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "frontend")
)


def create_app() -> Flask:
    app = Flask(__name__, static_folder=None)
    app.config.from_object(Config)

    CORS(app)
    db.init_app(app)

    # Registro dos blueprints (rotas da API)
    from routes.auth import auth_bp
    from routes.schedules import schedules_bp
    from routes.questions import questions_bp
    from routes.performance import performance_bp
    from routes.materials import materials_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(schedules_bp)
    app.register_blueprint(questions_bp)
    app.register_blueprint(performance_bp)
    app.register_blueprint(materials_bp)

    with app.app_context():
        db.create_all()

    @app.get("/api/health")
    def health():
        return jsonify(
            {
                "status": "ok",
                "service": "Study Time API",
                "database": app.config["SQLALCHEMY_DATABASE_URI"].split(":")[0],
            }
        )

    # ---- Servir o frontend estático ----
    @app.get("/")
    def index():
        return send_from_directory(FRONTEND_DIR, "index.html")

    @app.get("/<path:path>")
    def static_files(path):
        full = os.path.join(FRONTEND_DIR, path)
        if os.path.isfile(full):
            return send_from_directory(FRONTEND_DIR, path)
        # fallback para páginas sem extensão (ex.: /questoes)
        html = os.path.join(FRONTEND_DIR, f"{path}.html")
        if os.path.isfile(html):
            return send_from_directory(FRONTEND_DIR, f"{path}.html")
        return send_from_directory(FRONTEND_DIR, "index.html")

    return app


app = create_app()


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print("=" * 60)
    print("  Study Time - Plataforma auxiliar para estudos ENEM")
    print(f"  Servidor:  http://localhost:{port}")
    print(f"  Banco:     {app.config['SQLALCHEMY_DATABASE_URI'].split('://')[0]}")
    print("=" * 60)
    app.run(host="0.0.0.0", port=port, debug=True)
