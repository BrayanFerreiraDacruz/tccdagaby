"""
Rotas de autenticação e gerenciamento de conta.

RF01 - cadastro | RF02 - login | RF03 - gerenciar/excluir conta
"""
import re

from flask import Blueprint, g, jsonify, request

from auth_utils import generate_token, login_required
from models import User, db

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _valid_email(email: str) -> bool:
    return bool(EMAIL_RE.match(email or ""))


@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not name or len(name) < 2:
        return jsonify({"error": "Informe um nome válido."}), 400
    if not _valid_email(email):
        return jsonify({"error": "Informe um e-mail válido."}), 400
    if len(password) < 6:
        return jsonify({"error": "A senha deve ter ao menos 6 caracteres."}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Este e-mail já está cadastrado."}), 409

    user = User(name=name, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return (
        jsonify({"token": generate_token(user), "user": user.to_dict()}),
        201,
    )


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "E-mail ou senha incorretos."}), 401

    return jsonify({"token": generate_token(user), "user": user.to_dict()})


@auth_bp.get("/me")
@login_required
def me():
    return jsonify({"user": g.current_user.to_dict()})


@auth_bp.put("/me")
@login_required
def update_me():
    data = request.get_json(silent=True) or {}
    user = g.current_user

    name = (data.get("name") or "").strip()
    if name:
        if len(name) < 2:
            return jsonify({"error": "Informe um nome válido."}), 400
        user.name = name

    email = (data.get("email") or "").strip().lower()
    if email and email != user.email:
        if not _valid_email(email):
            return jsonify({"error": "Informe um e-mail válido."}), 400
        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Este e-mail já está em uso."}), 409
        user.email = email

    new_password = data.get("password")
    if new_password:
        if len(new_password) < 6:
            return jsonify({"error": "A senha deve ter ao menos 6 caracteres."}), 400
        user.set_password(new_password)

    db.session.commit()
    return jsonify({"user": user.to_dict()})


@auth_bp.delete("/me")
@login_required
def delete_me():
    user = g.current_user
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "Conta excluída com sucesso."})
