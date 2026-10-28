"""Module: audia.config.database.

Purpose: Build the existing PostgreSQL URL from environment settings.
Main components: build_database_url.
Related: app.py loads .env first; SQLAlchemy URL safely encodes credentials.
Debugging: Check DB_* availability and DATABASE_URL fallback without logging credentials.
"""
import os
from sqlalchemy import URL


def build_database_url():
    """
    Build the PostgreSQL URL from the separate
    credentials stored in .env.

    Falls back to DATABASE_URL if the separate
    credentials are not available.

    Returns a SQLAlchemy URL or the existing DATABASE_URL string.
    Missing individual credentials select the fallback; invalid DB_PORT raises
    ValueError during startup. app.py must load .env before calling this.
    """

    required_variables = (
        "DB_USER",
        "DB_PASSWORD",
        "DB_NAME",
    )

    if not all(
        os.getenv(name)
        for name in required_variables
    ):
        return os.getenv(
            "DATABASE_URL",
            "",
        )

    return URL.create(
        drivername="postgresql+psycopg",
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv(
            "DB_HOST",
            "localhost",
        ),
        port=int(
            os.getenv(
                "DB_PORT",
                "5432",
            )
        ),
        database=os.getenv("DB_NAME"),
    )
