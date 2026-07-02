from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.auth import CurrentUser, get_current_user
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


def test_account_settings_returns_saved_leetcode_username() -> None:
    session = create_test_session()
    LeetCodeSubmissionRepository(session).save_sync_result(
        user_id="user-1",
        username="kprashanth01",
        submissions=[
            LeetCodeSubmission(
                title="Two Sum",
                slug="two-sum",
                language="cpp",
                submitted_at=datetime(2026, 7, 1, 12, 0, tzinfo=timezone.utc),
            )
        ],
    )
    app.dependency_overrides[get_db] = override_db_session(session)
    app.dependency_overrides[get_current_user] = lambda: CurrentUser(
        id="user-1",
        email="user@example.com",
    )

    try:
        client = TestClient(app)
        response = client.get("/account/settings")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "leetcode_username": "kprashanth01",
        "email": "user@example.com",
    }


def test_account_settings_do_not_return_other_users_username() -> None:
    session = create_test_session()
    LeetCodeSubmissionRepository(session).save_sync_result(
        user_id="user-2",
        username="other-user",
        submissions=[
            LeetCodeSubmission(
                title="Two Sum",
                slug="two-sum",
                language="cpp",
                submitted_at=datetime(2026, 7, 1, 12, 0, tzinfo=timezone.utc),
            )
        ],
    )
    app.dependency_overrides[get_db] = override_db_session(session)
    app.dependency_overrides[get_current_user] = lambda: CurrentUser(
        id="user-1",
        email="user@example.com",
    )

    try:
        client = TestClient(app)
        response = client.get("/account/settings")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "leetcode_username": None,
        "email": "user@example.com",
    }


def test_account_settings_requires_authentication() -> None:
    client = TestClient(app)

    response = client.get("/account/settings")

    assert response.status_code == 401
