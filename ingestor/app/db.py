from contextlib import contextmanager

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Json

from app.config import settings


def connect():
    return psycopg.connect(settings.database_url, row_factory=dict_row, sslmode="disable")


@contextmanager
def db():
    conn = connect()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def vector_literal(values: list[float]) -> str:
    return "[" + ",".join(f"{v:.8f}" for v in values) + "]"


Jsonb = Json
