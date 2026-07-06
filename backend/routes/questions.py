"""
Rotas de questões do ENEM (integração com a API oficial ENEM.dev) e
verificação de respostas com registro de desempenho.

RF07 - resolver questões | RF08 - integração ENEM.dev
RF09 - verificar resposta | RF10 - registrar desempenho
"""
from flask import Blueprint, g, jsonify, request

import enem_client
from auth_utils import login_required
from enem_client import EnemApiError
from models import Attempt, db

questions_bp = Blueprint("questions", __name__, url_prefix="/api")


@questions_bp.get("/exams")
def exams():
    """Lista as provas disponíveis (anos, disciplinas, idiomas)."""
    try:
        return jsonify({"exams": enem_client.list_exams()})
    except EnemApiError as exc:
        return jsonify({"error": str(exc)}), 502


@questions_bp.get("/questions")
def questions():
    """Lista questões filtradas por ano/disciplina/idioma (sem gabarito)."""
    try:
        year = int(request.args.get("year", 2023))
    except ValueError:
        return jsonify({"error": "Ano inválido."}), 400

    discipline = request.args.get("discipline") or None
    language = request.args.get("language") or None
    try:
        limit = min(int(request.args.get("limit", 10)), 30)
        offset = max(int(request.args.get("offset", 0)), 0)
    except ValueError:
        return jsonify({"error": "Parâmetros de paginação inválidos."}), 400

    try:
        data = enem_client.get_questions(
            year, discipline, language, limit=limit, offset=offset
        )
        return jsonify(data)
    except EnemApiError as exc:
        return jsonify({"error": str(exc)}), 502


@questions_bp.get("/questions/<int:year>/<int:index>")
def single_question(year, index):
    language = request.args.get("language") or None
    try:
        return jsonify({"question": enem_client.get_question(year, index, language)})
    except EnemApiError as exc:
        return jsonify({"error": str(exc)}), 502


@questions_bp.post("/answer")
@login_required
def answer():
    """
    Recebe a resposta do usuário, verifica com o gabarito oficial e
    registra o desempenho no banco de dados.
    """
    data = request.get_json(silent=True) or {}
    try:
        year = int(data.get("year"))
        index = int(data.get("index"))
    except (TypeError, ValueError):
        return jsonify({"error": "Ano ou questão inválidos."}), 400

    chosen = (data.get("chosen") or "").strip().upper()
    if chosen not in {"A", "B", "C", "D", "E"}:
        return jsonify({"error": "Alternativa inválida."}), 400

    language = data.get("language") or None

    try:
        gabarito = enem_client.get_correct_alternative(year, index, language)
    except EnemApiError as exc:
        return jsonify({"error": str(exc)}), 502

    correct = gabarito["correct"]
    is_correct = chosen == correct

    attempt = Attempt(
        user_id=g.current_user.id,
        year=year,
        question_index=index,
        discipline=gabarito.get("discipline"),
        language=gabarito.get("language"),
        chosen=chosen,
        correct=correct,
        is_correct=is_correct,
    )
    db.session.add(attempt)
    db.session.commit()

    return jsonify(
        {
            "is_correct": is_correct,
            "correct": correct,
            "chosen": chosen,
        }
    )
