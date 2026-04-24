# src/docuview/db/__init__.py
"""
Пакет docuview.db — работа с базой данных.

Публичный API:
    ping() -> dict[str, str]   синхронная проверка соединения (используется в /health)
"""
from __future__ import annotations

import psycopg

from docuview.core.config import settings


def ping() -> dict[str, str]:
    """
    Синхронная проверка соединения с PostgreSQL.

    Выполняет SELECT version() и возвращает словарь с полем "version".
    Используется в GET /health для проверки готовности БД.

    Возвращает:
        {"version": "PostgreSQL 16.x on ..."}

    Raises:
        psycopg.OperationalError: если БД недоступна.
        psycopg.Error: при любой другой ошибке psycopg.
    """
    with psycopg.connect(settings.database_url_sync) as conn:
        row = conn.execute("SELECT version()").fetchone()
    version = row[0] if row else "unknown"
    return {"version": version}
