import pytest
import sqlite3
from pathlib import Path
from starlette.testclient import TestClient

from app.config import DEFAULT_DB_FILE
from app.database import Base, SessionLocal, engine
from app.main import app
from data.seed import seed_database


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Ensure the catalog database is properly initialized and seeded before any tests run."""
    seed_database(force=False)
    yield


@pytest.fixture
def db_session():
    """Yield a database session for testing."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client():
    """Return a Starlette TestClient for the application."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def catalog_db_path() -> Path:
    """Return path to catalog.db."""
    return DEFAULT_DB_FILE
