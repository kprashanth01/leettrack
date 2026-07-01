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
from app.schemas import LeetCodeProblemMetadata, LeetCodeSubmission


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


def seed_synced_problem(session: Session, user_id: str = "user-1") -> None:
    LeetCodeSubmissionRepository(session).save_sync_result(
        user_id=user_id,
        username="kprashanth01",
        submissions=[
            LeetCodeSubmission(
                title="Two Sum",
                slug="two-sum",
                language="python3",
                submitted_at=datetime(2026, 7, 1, 12, 0, tzinfo=timezone.utc),
            )
        ],
        metadata_by_slug={
            "two-sum": LeetCodeProblemMetadata(
                slug="two-sum",
                difficulty="Easy",
                topic_tags=["Array", "Hash Table"],
            )
        },
    )


def test_notes_endpoint_creates_lists_updates_and_deletes_owned_note() -> None:
    session = create_test_session()
    seed_synced_problem(session)
    app.dependency_overrides[get_db] = override_db_session(session)
    app.dependency_overrides[get_current_user] = lambda: CurrentUser(
        id="user-1",
        email="user@example.com",
    )

    try:
        client = TestClient(app)
        create_response = client.post(
            "/notes",
            json={
                "problem_slug": "two-sum",
                "content": "Use a hash map and watch duplicate values.",
            },
        )
        note_id = create_response.json()["id"]
        list_response = client.get("/notes")
        update_response = client.patch(
            f"/notes/{note_id}",
            json={"content": "Hash map complements; remember duplicate values."},
        )
        delete_response = client.delete(f"/notes/{note_id}")
        empty_list_response = client.get("/notes")
    finally:
        app.dependency_overrides.clear()

    assert create_response.status_code == 201
    assert create_response.json()["problem_slug"] == "two-sum"
    assert create_response.json()["problem_title"] == "Two Sum"
    assert create_response.json()["difficulty"] == "Easy"
    assert create_response.json()["topic_tags"] == ["Array", "Hash Table"]
    assert list_response.status_code == 200
    assert len(list_response.json()["notes"]) == 1
    assert update_response.status_code == 200
    assert (
        update_response.json()["content"]
        == "Hash map complements; remember duplicate values."
    )
    assert delete_response.status_code == 204
    assert empty_list_response.json() == {"notes": []}


def test_notes_endpoint_rejects_notes_for_unsynced_problem() -> None:
    session = create_test_session()
    app.dependency_overrides[get_db] = override_db_session(session)
    app.dependency_overrides[get_current_user] = lambda: CurrentUser(
        id="user-1",
        email="user@example.com",
    )

    try:
        client = TestClient(app)
        response = client.post(
            "/notes",
            json={"problem_slug": "two-sum", "content": "No synced problem yet."},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json()["detail"] == "Sync this LeetCode problem before adding notes."


def test_notes_endpoint_isolates_notes_by_user() -> None:
    session = create_test_session()
    seed_synced_problem(session, user_id="user-1")
    seed_synced_problem(session, user_id="user-2")
    app.dependency_overrides[get_db] = override_db_session(session)

    client = TestClient(app)
    try:
        app.dependency_overrides[get_current_user] = lambda: CurrentUser(
            id="user-1",
            email="first@example.com",
        )
        create_response = client.post(
            "/notes",
            json={"problem_slug": "two-sum", "content": "Visible to user one."},
        )
        note_id = create_response.json()["id"]

        app.dependency_overrides[get_current_user] = lambda: CurrentUser(
            id="user-2",
            email="second@example.com",
        )
        list_response = client.get("/notes")
        update_response = client.patch(
            f"/notes/{note_id}",
            json={"content": "Trying to overwrite another user's note."},
        )
        delete_response = client.delete(f"/notes/{note_id}")
    finally:
        app.dependency_overrides.clear()

    assert create_response.status_code == 201
    assert list_response.json() == {"notes": []}
    assert update_response.status_code == 404
    assert delete_response.status_code == 404


def test_notes_endpoint_requires_authentication() -> None:
    client = TestClient(app)

    response = client.get("/notes")

    assert response.status_code == 401
