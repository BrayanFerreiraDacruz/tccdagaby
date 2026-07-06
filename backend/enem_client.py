"""
Cliente da API oficial ENEM.dev (https://enem.dev / https://api.enem.dev).

Fornece as questões REAIS e oficiais das provas do ENEM (2009 a 2023),
atendendo aos requisitos RF07, RF08 e RS05 do projeto.

Para não exigir armazenamento local de um banco de questões (conforme a
arquitetura definida no TCC), este módulo consulta a API pública e mantém um
cache em memória com TTL para reduzir latência (RNF03) e o número de requisições.
"""
import time
from threading import Lock

import requests
from flask import current_app

# cache: { chave: (timestamp, dados) }
_cache: dict = {}
_cache_lock = Lock()
_CACHE_TTL = 60 * 30  # 30 minutos

REQUEST_TIMEOUT = 15


def _base() -> str:
    return current_app.config["ENEM_API_BASE"].rstrip("/")


def _cache_get(key: str):
    with _cache_lock:
        item = _cache.get(key)
        if item and (time.time() - item[0] < _CACHE_TTL):
            return item[1]
    return None


def _cache_set(key: str, value) -> None:
    with _cache_lock:
        _cache[key] = (time.time(), value)


class EnemApiError(Exception):
    """Erro ao consultar a API ENEM.dev."""


def _get(url: str, params: dict | None = None):
    try:
        resp = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
    except requests.RequestException as exc:
        raise EnemApiError(f"Falha de conexão com a API ENEM.dev: {exc}") from exc

    if resp.status_code == 404:
        raise EnemApiError("Conteúdo não encontrado na API ENEM.dev.")
    if resp.status_code == 429:
        raise EnemApiError("Limite de requisições atingido. Tente novamente em instantes.")
    if not resp.ok:
        raise EnemApiError(f"API ENEM.dev retornou status {resp.status_code}.")

    return resp.json()


def list_exams() -> list:
    """Lista todas as provas disponíveis (anos, disciplinas e idiomas)."""
    cached = _cache_get("exams")
    if cached is not None:
        return cached
    data = _get(f"{_base()}/exams")
    _cache_set("exams", data)
    return data


def _fetch_all_questions(year: int, language: str | None) -> list:
    """Busca (paginado) todas as questões de uma prova e mantém em cache."""
    key = f"all:{year}:{language or 'default'}"
    cached = _cache_get(key)
    if cached is not None:
        return cached

    questions: list = []
    offset = 0
    limit = 50
    while True:
        params = {"limit": limit, "offset": offset}
        if language:
            params["language"] = language
        data = _get(f"{_base()}/exams/{year}/questions", params=params)
        batch = data.get("questions", [])
        questions.extend(batch)
        meta = data.get("metadata", {})
        if not meta.get("hasMore") or not batch:
            break
        offset += limit

    _cache_set(key, questions)
    return questions


def _strip_answer(question: dict) -> dict:
    """Remove o gabarito antes de enviar a questão ao frontend (anti-cola)."""
    q = dict(question)
    q.pop("correctAlternative", None)
    q["alternatives"] = [
        {"letter": a.get("letter"), "text": a.get("text"), "file": a.get("file")}
        for a in question.get("alternatives", [])
    ]
    return q


def get_questions(
    year: int,
    discipline: str | None = None,
    language: str | None = None,
    limit: int = 10,
    offset: int = 0,
) -> dict:
    """
    Retorna questões da prova filtradas por disciplina, SEM o gabarito.
    A verificação da resposta é feita apenas no backend (get_correct_alternative).
    """
    all_q = _fetch_all_questions(year, language)

    if discipline:
        filtered = [q for q in all_q if q.get("discipline") == discipline]
    else:
        filtered = all_q

    total = len(filtered)
    page = filtered[offset : offset + limit]
    return {
        "metadata": {
            "year": year,
            "discipline": discipline,
            "language": language,
            "limit": limit,
            "offset": offset,
            "total": total,
            "hasMore": offset + limit < total,
        },
        "questions": [_strip_answer(q) for q in page],
    }


def get_question(year: int, index: int, language: str | None = None) -> dict:
    """Retorna uma única questão (sem gabarito) por ano e índice."""
    key = f"q:{year}:{index}:{language or 'default'}"
    cached = _cache_get(key)
    if cached is None:
        params = {"language": language} if language else None
        cached = _get(f"{_base()}/exams/{year}/questions/{index}", params)
        _cache_set(key, cached)
    return _strip_answer(cached)


def get_correct_alternative(
    year: int, index: int, language: str | None = None
) -> dict:
    """
    Consulta o gabarito oficial de uma questão (usado na verificação de resposta).
    Retorna { correct, discipline, language }.
    """
    key = f"q:{year}:{index}:{language or 'default'}"
    cached = _cache_get(key)
    if cached is None:
        params = {"language": language} if language else None
        cached = _get(f"{_base()}/exams/{year}/questions/{index}", params)
        _cache_set(key, cached)
    return {
        "correct": cached.get("correctAlternative"),
        "discipline": cached.get("discipline"),
        "language": cached.get("language"),
    }
