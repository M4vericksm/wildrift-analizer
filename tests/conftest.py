import os
import tempfile

import pytest

_tmp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp_db.name}"
os.environ.setdefault("GEMINI_API_KEY", "test-key")


@pytest.fixture(scope="session", autouse=True)
def _create_tables():
    from core import models  # noqa: F401 — registra os modelos no Base
    from core.db import Base, engine

    Base.metadata.create_all(bind=engine)


@pytest.fixture
def client():
    from fastapi.testclient import TestClient

    from backend.main import app

    return TestClient(app)
