"""
Utilitários de autenticação: geração/validação de token JWT e o decorator
`login_required`, que protege as rotas privadas da API (RNF04 - segurança).
"""
from datetime import datetime, timedelta
from functools import wraps

import jwt
from flask import current_app, g, jsonify, request

from models import User


def generate_token(user: User) -> str:
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "exp": datetime.utcnow()
        + timedelta(hours=current_app.config["JWT_EXP_HOURS"]),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")


def decode_token(token: str):
    try:
        return jwt.decode(
            token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
        )
    except jwt.PyJWTError:
        return None


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify({"error": "Token ausente. Faça login novamente."}), 401

        payload = decode_token(auth.split(" ", 1)[1])
        if not payload:
            return jsonify({"error": "Sessão expirada. Faça login novamente."}), 401

        user = User.query.get(int(payload["sub"]))
        if not user:
            return jsonify({"error": "Usuário não encontrado."}), 401

        g.current_user = user
        return fn(*args, **kwargs)

    return wrapper
