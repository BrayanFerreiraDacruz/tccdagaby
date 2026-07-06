"""
Rotas de cronograma de estudos personalizado.

RF04 - criar | RF05 - editar/excluir | RF06 - exibir | RF13 - organizar tempo
"""
from flask import Blueprint, g, jsonify, request

from auth_utils import login_required
from models import Schedule, db

schedules_bp = Blueprint("schedules", __name__, url_prefix="/api/schedules")

TIME_RE = __import__("re").compile(r"^([01]\d|2[0-3]):[0-5]\d$")


def _validate(data: dict):
    title = (data.get("title") or "").strip()
    if not title:
        return None, "Informe um título para o bloco de estudo."

    try:
        weekday = int(data.get("weekday"))
    except (TypeError, ValueError):
        return None, "Dia da semana inválido."
    if weekday < 0 or weekday > 6:
        return None, "Dia da semana inválido."

    start = (data.get("start_time") or "").strip()
    end = (data.get("end_time") or "").strip()
    if not TIME_RE.match(start) or not TIME_RE.match(end):
        return None, "Horário inválido (use o formato HH:MM)."
    if end <= start:
        return None, "O horário de término deve ser após o de início."

    return {
        "title": title,
        "discipline": (data.get("discipline") or "").strip() or None,
        "weekday": weekday,
        "start_time": start,
        "end_time": end,
        "notes": (data.get("notes") or "").strip() or None,
    }, None


@schedules_bp.get("")
@login_required
def list_schedules():
    items = (
        Schedule.query.filter_by(user_id=g.current_user.id)
        .order_by(Schedule.weekday, Schedule.start_time)
        .all()
    )
    return jsonify({"schedules": [s.to_dict() for s in items]})


@schedules_bp.post("")
@login_required
def create_schedule():
    fields, error = _validate(request.get_json(silent=True) or {})
    if error:
        return jsonify({"error": error}), 400

    schedule = Schedule(user_id=g.current_user.id, **fields)
    db.session.add(schedule)
    db.session.commit()
    return jsonify({"schedule": schedule.to_dict()}), 201


@schedules_bp.put("/<int:schedule_id>")
@login_required
def update_schedule(schedule_id):
    schedule = Schedule.query.filter_by(
        id=schedule_id, user_id=g.current_user.id
    ).first()
    if not schedule:
        return jsonify({"error": "Cronograma não encontrado."}), 404

    fields, error = _validate(request.get_json(silent=True) or {})
    if error:
        return jsonify({"error": error}), 400

    for key, value in fields.items():
        setattr(schedule, key, value)
    db.session.commit()
    return jsonify({"schedule": schedule.to_dict()})


@schedules_bp.delete("/<int:schedule_id>")
@login_required
def delete_schedule(schedule_id):
    schedule = Schedule.query.filter_by(
        id=schedule_id, user_id=g.current_user.id
    ).first()
    if not schedule:
        return jsonify({"error": "Cronograma não encontrado."}), 404

    db.session.delete(schedule)
    db.session.commit()
    return jsonify({"message": "Bloco de estudo removido."})
