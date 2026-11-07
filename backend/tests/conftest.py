import pytest

from backend.app.db import init_db


@pytest.fixture(autouse=True)
def setup_test_db():
    init_db()
