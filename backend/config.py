"""
Configuração central da aplicação Study Time.

Segue o RS04 do projeto (MySQL como banco de dados). Para garantir que a
plataforma rode mesmo sem o XAMPP ativo durante os testes, há um fallback
automático para SQLite — o esquema das tabelas é idêntico.
"""
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def _build_database_uri() -> str:
    """Monta a URI do banco. Tenta MySQL (XAMPP); cai para SQLite se falhar."""
    use_mysql = os.getenv("USE_MYSQL", "true").lower() == "true"

    if use_mysql:
        host = os.getenv("MYSQL_HOST", "localhost")
        port = os.getenv("MYSQL_PORT", "3306")
        user = os.getenv("MYSQL_USER", "root")
        password = os.getenv("MYSQL_PASSWORD", "")
        database = os.getenv("MYSQL_DATABASE", "study_time")

        try:
            import pymysql

            # Garante que o banco exista (útil no primeiro uso com XAMPP)
            conn = pymysql.connect(
                host=host, port=int(port), user=user, password=password
            )
            with conn.cursor() as cursor:
                cursor.execute(
                    f"CREATE DATABASE IF NOT EXISTS {database} "
                    "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                )
            conn.close()

            return (
                f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
                "?charset=utf8mb4"
            )
        except Exception as exc:  # noqa: BLE001
            print(
                "[Study Time] MySQL indisponível "
                f"({exc.__class__.__name__}). Usando SQLite como fallback."
            )

    sqlite_path = os.path.join(BASE_DIR, "study_time.db")
    return f"sqlite:///{sqlite_path}"


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    SQLALCHEMY_DATABASE_URI = _build_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ENEM_API_BASE = os.getenv("ENEM_API_BASE", "https://api.enem.dev/v1")

    # Duração do token de sessão (em horas)
    JWT_EXP_HOURS = 24 * 7
