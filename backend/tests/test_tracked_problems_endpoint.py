from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.auth import CurrentUser, get_current_user
from app.database import get_db
from app.leetcode_client import LeetCodeClientError
from app.main import app
from app.models import Base
from app.routes.problems import get_problem_metadata_client
from app.schemas import LeetCodeProblemMetadata


class FakeMetadataClient:
    def fetch_problem_metadata(self, slug: str) -> LeetCodeProblemMetadata | None:
        return LeetCodeProblemMetadata(
            slug=slug,
            difficulty="Medium",
            topic_tags=["Linked List", "Math", "Recursion"],
        )


class FailingMetadataClient:
    def fetch_problem_metadata(self, slug: str) -> LeetCodeProblemMetadata | None:
        raise LeetCodeClientError("metadata unavailable")


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


def test_tracked_problems_endpoint_saves_and_lists_extension_problem() -> None:
    session = create_test_session()
    app.dependency_overrides[get_db] = override_db_session(session)
    app.dependency_overrides[get_current_user] = lambda: CurrentUser(
        id="user-1",
        email="user@example.com",
    )

    try:
        client = TestClient(app)
        create_response = client.post(
            "/problems/tracked",
            json={
                "problem_slug": "two-sum",
                "problem_title": "Two Sum",
                "source": "extension",
            },
        )
        list_response = client.get("/problems/tracked")
    finally:
        app.dependency_overrides.clear()

    assert create_response.status_code == 201
    assert create_response.json()["is_new"] is True
    assert create_response.json()["problem"]["problem_slug"] == "two-sum"
    assert create_response.json()["problem"]["problem_title"] == "Two Sum"
    assert list_response.status_code == 200
    assert len(list_response.json()["problems"]) == 1
    assert list_response.json()["problems"][0]["problem_slug"] == "two-sum"


def test_tracked_problems_endpoint_enriches_saved_problem_with_metadata() -> None:
    session = create_test_session()
    app.dependency_overrides[get_db] = override_db_session(session)
    app.dependency_overrides[get_current_user] = lambda: CurrentUser(
        id="user-1",
        email="user@example.com",
    )
    app.dependency_overrides[get_problem_metadata_client] = lambda: FakeMetadataClient()

    try:
        client = TestClient(app)
        create_response = client.post(
            "/problems/tracked",
            json={
                "problem_slug": "add-two-numbers",
                "problem_title": "Add Two Numbers",
                "source": "extension",
            },
        )
        list_response = client.get("/problems/tracked")
    finally:
        app.dependency_overrides.clear()

    assert create_response.status_code == 201
    assert create_response.json()["problem"]["difficulty"] == "Medium"
    assert create_response.json()["problem"]["topic_tags"] == [
        "Linked List",
        "Math",
        "Recursion",
    ]
    assert list_response.json()["problems"][0]["difficulty"] == "Medium"


def test_tracked_problems_endpoint_saves_when_metadata_fetch_fails() -> None:
    session = create_test_session()
    app.dependency_overrides[get_db] = override_db_session(session)
    app.dependency_overrides[get_current_user] = lambda: CurrentUser(
        id="user-1",
        email="user@example.com",
    )
    app.dependency_overrides[get_problem_metadata_client] = lambda: FailingMetadataClient()

    try:
        client = TestClient(app)
        response = client.post(
            "/problems/tracked",
            json={
                "problem_slug": "add-two-numbers",
                "problem_title": "Add Two Numbers",
                "source": "extension",
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    assert response.json()["problem"]["problem_slug"] == "add-two-numbers"
    assert response.json()["problem"]["difficulty"] is None
    assert response.json()["problem"]["topic_tags"] == []


def test_tracked_problems_endpoint_is_idempotent_for_duplicate_save() -> None:
    session = create_test_session()
    app.dependency_overrides[get_db] = override_db_session(session)
    app.dependency_overrides[get_current_user] = lambda: CurrentUser(
        id="user-1",
        email="user@example.com",
    )

    try:
        client = TestClient(app)
        first_response = client.post(
            "/problems/tracked",
            json={
                "problem_slug": "two-sum",
                "problem_title": "Two Sum",
                "source": "extension",
            },
        )
        second_response = client.post(
            "/problems/tracked",
            json={
                "problem_slug": "two-sum",
                "problem_title": "Two Sum",
                "source": "extension",
            },
        )
        list_response = client.get("/problems/tracked")
    finally:
        app.dependency_overrides.clear()

    assert first_response.status_code == 201
    assert second_response.status_code == 200
    assert second_response.json()["is_new"] is False
    assert first_response.json()["problem"]["id"] == second_response.json()["problem"]["id"]
    assert len(list_response.json()["problems"]) == 1


def test_tracked_problems_endpoint_isolates_saved_problems_by_user() -> None:
    session = create_test_session()
    app.dependency_overrides[get_db] = override_db_session(session)
    client = TestClient(app)

    try:
        app.dependency_overrides[get_current_user] = lambda: CurrentUser(
            id="user-1",
            email="first@example.com",
        )
        create_response = client.post(
            "/problems/tracked",
            json={
                "problem_slug": "two-sum",
                "problem_title": "Two Sum",
                "source": "extension",
            },
        )

        app.dependency_overrides[get_current_user] = lambda: CurrentUser(
            id="user-2",
            email="second@example.com",
        )
        list_response = client.get("/problems/tracked")
    finally:
        app.dependency_overrides.clear()

    assert create_response.status_code == 201
    assert list_response.json() == {"problems": []}


def test_tracked_problems_endpoint_requires_authentication() -> None:
    client = TestClient(app)

    response = client.get("/problems/tracked")

    assert response.status_code == 401
