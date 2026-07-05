"""Acceso a Postgres (Supabase) para la API: conexión por request + helpers."""

from contextlib import contextmanager

import psycopg
from psycopg.rows import dict_row

from src.common import database_url


@contextmanager
def get_conn():
    conn = psycopg.connect(database_url(), connect_timeout=15, row_factory=dict_row)
    try:
        yield conn
    finally:
        conn.close()


def query(sql: str, params=None) -> list[dict]:
    with get_conn() as conn:
        return conn.execute(sql, params or ()).fetchall()


def query_one(sql: str, params=None) -> dict | None:
    filas = query(sql, params)
    return filas[0] if filas else None


def ensure_unaccent() -> None:
    """La búsqueda usa unaccent(); se crea la extensión si no existe (idempotente)."""
    try:
        with get_conn() as conn:
            conn.execute("CREATE EXTENSION IF NOT EXISTS unaccent")
            conn.commit()
    except Exception as e:  # noqa: BLE001 — sin unaccent la búsqueda sigue con ILIKE simple
        print(f"[db] unaccent no disponible: {e}")
