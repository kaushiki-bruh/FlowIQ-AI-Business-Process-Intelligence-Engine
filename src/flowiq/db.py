"""
db.py

Why it exists:
    Every other module needs a Postgres connection. Centralizing it
    here means credentials live in one place (.env) and no other file
    has to know connection details.

What problem it solves:
    Avoids repeating psycopg2.connect(...) with hardcoded credentials
    in every script — and keeps secrets out of version control.

Inputs:
    None directly — reads DB_HOST, DB_PORT, DB_NAME, DB_USER,
    DB_PASSWORD from environment variables (loaded from .env).

Outputs:
    get_connection() -> psycopg2 connection object, ready to use.
"""

import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    """Open and return a new psycopg2 connection using .env credentials."""
    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        port=os.environ.get("DB_PORT", "5432"),
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    )
