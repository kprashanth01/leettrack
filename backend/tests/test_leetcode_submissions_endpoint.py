from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.database import get_db
from app.main import app
from app.models import Base
from app.repositories import LeetCodeSubmissionRepository
from app.schemas import LeetCodeSubmission


def override_db_session(session: Session):
    def _override_db():
        yield session

    return _override_db


def create_test_session() -> Session:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    return Session(engine)


def test_submissions_endpoint_returns_persisted_submissions_for_username() -> None:
    session = create_test_session()
    repository = LeetCodeSubmissionRepository(session)
    repository.save_sync_result(
        username="kprashanth01",
        submissions=[
            LeetCodeSubmission(
                title="Two Sum",
                slug="two-sum",
                language="python3",
                submitted_at=datetime(2026, 7, 1, 12, 0, tzinfo=timezone.utc),
            )
        ],
    )
    app.dependency_overrides[get_db] = override_db_session(session)

    try:
        client = TestClient(app)
        response = client.get("/leetcode/submissions?username=kprashanth01")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "username": "kprashanth01",
        "submissions": [
            {
                "title": "Two Sum",
                "slug": "two-sum",
                "language": "python3",
                "submitted_at": "2026-07-01T12:00:00Z",
                "source": "leetcode",
            }
        ],
    }


def test_submissions_endpoint_rejects_invalid_username() -> None:
    client = TestClient(app)

    response = client.get("/leetcode/submissions?username=   ")

    assert response.status_code == 422
