"""
Rotas de desempenho e progresso do usuário.

RF10 - registrar desempenho | RF11 - visualizar progresso
"""
from collections import defaultdict

from flask import Blueprint, g, jsonify

from auth_utils import login_required
from models import Attempt

performance_bp = Blueprint("performance", __name__, url_prefix="/api/performance")

DISCIPLINE_LABELS = {
    "linguagens": "Linguagens e Códigos",
    "ciencias-humanas": "Ciências Humanas",
    "ciencias-natureza": "Ciências da Natureza",
    "matematica": "Matemática",
}


@performance_bp.get("/summary")
@login_required
def summary():
    attempts = Attempt.query.filter_by(user_id=g.current_user.id).all()

    total = len(attempts)
    correct = sum(1 for a in attempts if a.is_correct)
    accuracy = round((correct / total) * 100, 1) if total else 0.0

    by_disc = defaultdict(lambda: {"total": 0, "correct": 0})
    for a in attempts:
        key = a.discipline or "outros"
        by_disc[key]["total"] += 1
        if a.is_correct:
            by_disc[key]["correct"] += 1

    disciplines = []
    for key, val in by_disc.items():
        disciplines.append(
            {
                "discipline": key,
                "label": DISCIPLINE_LABELS.get(key, key.title()),
                "total": val["total"],
                "correct": val["correct"],
                "accuracy": round((val["correct"] / val["total"]) * 100, 1)
                if val["total"]
                else 0.0,
            }
        )
    disciplines.sort(key=lambda d: d["total"], reverse=True)

    return jsonify(
        {
            "total": total,
            "correct": correct,
            "wrong": total - correct,
            "accuracy": accuracy,
            "disciplines": disciplines,
        }
    )


@performance_bp.get("/history")
@login_required
def history():
    attempts = (
        Attempt.query.filter_by(user_id=g.current_user.id)
        .order_by(Attempt.answered_at.desc())
        .limit(50)
        .all()
    )
    return jsonify({"history": [a.to_dict() for a in attempts]})
