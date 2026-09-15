import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.database import engine
from app.db.session import get_db
from app.main import app


@pytest.fixture
def client() -> TestClient:
    connection = engine.connect()
    transaction = connection.begin()

    session = Session(
        bind=connection,
        join_transaction_mode="create_savepoint",
    )

    def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)
        session.close()
        transaction.rollback()
        connection.close()