from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.auth import CurrentUser, get_current_user
from app.leetcode_client import LeetCodeClientError
from app.main import app
from app.routes.leetcode import get_leetcode_sync_service
from app.schemas import LeetCodeSubmission, LeetCodeSyncResult


class FakeSyncService:
    def __init__(self) -> None:
        self.last_user_id: str | None = None
        self.last_username: str | None = None
        self.last_limit: int | None = None

    def sync_recent_accepted_submissions(
        self, user_id: str, username: str, limit: int
    ) -> LeetCodeSyncResult:
        self.last_user_id = user_id
        self.last_username = username
        self.last_limit = limit
        submissions = [
            LeetCodeSubmission(
                title="Two Sum",
                slug="two-sum",
                language="python3",
                submitted_at=datetime(2026, 7, 1, 12, 0, tzinfo=timezone.utc),
                source="leetcode",
            )
        ]
        return LeetCodeSyncResult(
            username=username,
            fetched_count=1,
            saved_count=1,
            submissions=submissions,
        )


class FailingSyncService:
    def sync_recent_accepted_submissions(
        self, user_id: str, username: str, limit: int
    ) -> LeetCodeSyncResult:
        raise LeetCodeClientError("LeetCode is unavailable")


def test_sync_endpoint_returns_normalized_recent_accepted_submissions() -> None:
    fake_service = FakeSyncService()
    app.dependency_overrides[get_leetcode_sync_service] = lambda: fake_service
    app.dependency_overrides[get_current_user] = lambda: CurrentUser(
        id="user-1",
        email="user@example.com",
    )

    try:
        client = TestClient(app)
        response = client.post(
            "/leetcode/sync",
            json={"username": "kprashanth01", "limit": 5},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "status": "completed",
        "username": "kprashanth01",
        "fetched_count": 1,
        "saved_count": 1,
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
    assert fake_service.last_user_id == "user-1"
    assert fake_service.last_username == "kprashanth01"
    assert fake_service.last_limit == 5


def test_sync_endpoint_requires_authentication() -> None:
    client = TestClient(app)

    response = client.post(
        "/leetcode/sync",
        json={"username": "kprashanth01", "limit": 5},
    )

    assert response.status_code == 401


def test_sync_endpoint_rejects_invalid_username() -> None:
    app.dependency_overrides[get_current_user] = lambda: CurrentUser(
        id="user-1",
        email="user@example.com",
    )
    client = TestClient(app)

    try:
        response = client.post(
            "/leetcode/sync",
            json={"username": "   ", "limit": 5},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 422


def test_sync_endpoint_rejects_too_large_limit() -> None:
    app.dependency_overrides[get_current_user] = lambda: CurrentUser(
        id="user-1",
        email="user@example.com",
    )
    client = TestClient(app)

    try:
        response = client.post(
            "/leetcode/sync",
            json={"username": "kprashanth01", "limit": 100},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 422


def test_sync_endpoint_returns_502_when_leetcode_call_fails() -> None:
    app.dependency_overrides[get_leetcode_sync_service] = lambda: FailingSyncService()
    app.dependency_overrides[get_current_user] = lambda: CurrentUser(
        id="user-1",
        email="user@example.com",
    )

    try:
        client = TestClient(app)
        response = client.post(
            "/leetcode/sync",
            json={"username": "kprashanth01", "limit": 5},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 502
    assert response.json() == {
        "detail": "Could not sync with LeetCode. Please try again later."
    }
