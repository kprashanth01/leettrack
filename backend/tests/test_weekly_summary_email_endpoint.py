from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.auth import CurrentUser, get_current_user
from app.database import get_db
from app.main import app
from app.models import Base, EmailDeliveryAttempt
from app.repositories import (
    EmailPreferenceRepository,
    LeetCodeSubmissionRepository,
    ProblemNoteRepository,
)
from app.routes.emails import get_email_sender
from app.schemas import LeetCodeProblemMetadata, LeetCodeSubmission


class FakeEmailSender:
    def __init__(self) -> None:
        self.sent_messages: list[dict[str, str]] = []

    def send_email(self, to_email: str, subject: str, html: str) -> str:
        self.sent_messages.append(
            {
                "to_email": to_email,
                "subject": subject,
                "html": html,
            }
        )
        return "email_test_123"


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


def seed_user_activity(session: Session) -> None:
    LeetCodeSubmissionRepository(session).save_sync_result(
        user_id="user-1",
        username="kprashanth01",
        submissions=[
            LeetCodeSubmission(
                title="Two Sum",
                slug="two-sum",
                language="cpp",
                submitted_at=datetime(2026, 7, 1, 12, 0, tzinfo=timezone.utc),
            ),
            LeetCodeSubmission(
                title="Add Two Numbers",
                slug="add-two-numbers",
                language="cpp",
                submitted_at=datetime(2026, 7, 2, 10, 30, tzinfo=timezone.utc),
            ),
        ],
        metadata_by_slug={
            "two-sum": LeetCodeProblemMetadata(
                slug="two-sum",
                difficulty="Easy",
                topic_tags=["Array", "Hash Table"],
            ),
            "add-two-numbers": LeetCodeProblemMetadata(
                slug="add-two-numbers",
                difficulty="Medium",
                topic_tags=["Linked List", "Math"],
            ),
        },
    )
    ProblemNoteRepository(session).create_note(
        user_id="user-1",
        problem_slug="two-sum",
        content="Remember complement lookup.",
    )


def opt_in_user(session: Session, user_id: str, recipient_email: str) -> None:
    EmailPreferenceRepository(session).update_weekly_summary(
        user_id=user_id,
        weekly_summary_enabled=True,
        recipient_email=recipient_email,
    )


def test_weekly_summary_email_sends_to_authenticated_user() -> None:
    session = create_test_session()
    seed_user_activity(session)
    fake_sender = FakeEmailSender()
    app.dependency_overrides[get_db] = override_db_session(session)
    app.dependency_overrides[get_current_user] = lambda: CurrentUser(
        id="user-1",
        email="user@example.com",
    )
    app.dependency_overrides[get_email_sender] = lambda: fake_sender

    try:
        client = TestClient(app)
        response = client.post("/emails/weekly-summary")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 202
    assert response.json() == {
        "status": "sent",
        "email_id": "email_test_123",
        "recipient": "user@example.com",
    }
    assert len(fake_sender.sent_messages) == 1
    sent_message = fake_sender.sent_messages[0]
    assert sent_message["to_email"] == "user@example.com"
    assert sent_message["subject"] == "Your LeetTrack weekly summary"
    assert "LeetTrack Weekly Report" in sent_message["html"]
    assert "Recommended focus" in sent_message["html"]
    assert "2 accepted submissions" in sent_message["html"]
    assert "Two Sum" in sent_message["html"]
    assert "Remember complement lookup." in sent_message["html"]


def test_weekly_summary_email_uses_email_client_safe_layout() -> None:
    session = create_test_session()
    seed_user_activity(session)
    fake_sender = FakeEmailSender()
    app.dependency_overrides[get_db] = override_db_session(session)
    app.dependency_overrides[get_current_user] = lambda: CurrentUser(
        id="user-1",
        email="user@example.com",
    )
    app.dependency_overrides[get_email_sender] = lambda: fake_sender

    try:
        client = TestClient(app)
        response = client.post("/emails/weekly-summary")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 202
    html = fake_sender.sent_messages[0]["html"]
    assert "role=\"presentation\"" in html
    assert "display:grid" not in html


def test_weekly_summary_email_does_not_include_other_users_data() -> None:
    session = create_test_session()
    seed_user_activity(session)
    LeetCodeSubmissionRepository(session).save_sync_result(
        user_id="user-2",
        username="other",
        submissions=[
            LeetCodeSubmission(
                title="Secret Other Problem",
                slug="secret-other-problem",
                language="python3",
                submitted_at=datetime(2026, 7, 2, 14, 0, tzinfo=timezone.utc),
            )
        ],
    )
    fake_sender = FakeEmailSender()
    app.dependency_overrides[get_db] = override_db_session(session)
    app.dependency_overrides[get_current_user] = lambda: CurrentUser(
        id="user-1",
        email="user@example.com",
    )
    app.dependency_overrides[get_email_sender] = lambda: fake_sender

    try:
        client = TestClient(app)
        response = client.post("/emails/weekly-summary")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 202
    assert "Secret Other Problem" not in fake_sender.sent_messages[0]["html"]


def test_weekly_summary_email_requires_authentication() -> None:
    client = TestClient(app)

    response = client.post("/emails/weekly-summary")

    assert response.status_code == 401


def test_email_preferences_default_to_weekly_disabled() -> None:
    session = create_test_session()
    app.dependency_overrides[get_db] = override_db_session(session)
    app.dependency_overrides[get_current_user] = lambda: CurrentUser(
        id="user-1",
        email="user@example.com",
    )

    try:
        client = TestClient(app)
        response = client.get("/emails/preferences")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "weekly_summary_enabled": False,
        "recipient": "user@example.com",
    }


def test_email_preferences_can_be_updated_by_authenticated_user() -> None:
    session = create_test_session()
    app.dependency_overrides[get_db] = override_db_session(session)
    app.dependency_overrides[get_current_user] = lambda: CurrentUser(
        id="user-1",
        email="user@example.com",
    )

    try:
        client = TestClient(app)
        update_response = client.patch(
            "/emails/preferences",
            json={"weekly_summary_enabled": True},
        )
        get_response = client.get("/emails/preferences")
    finally:
        app.dependency_overrides.clear()

    assert update_response.status_code == 200
    assert update_response.json() == {
        "weekly_summary_enabled": True,
        "recipient": "user@example.com",
    }
    assert get_response.json()["weekly_summary_enabled"] is True


def test_email_preferences_are_scoped_to_authenticated_user() -> None:
    session = create_test_session()
    app.dependency_overrides[get_db] = override_db_session(session)
    app.dependency_overrides[get_current_user] = lambda: CurrentUser(
        id="user-1",
        email="user@example.com",
    )

    try:
        client = TestClient(app)
        client.patch(
            "/emails/preferences",
            json={"weekly_summary_enabled": True},
        )
        app.dependency_overrides[get_current_user] = lambda: CurrentUser(
            id="user-2",
            email="other@example.com",
        )
        other_user_response = client.get("/emails/preferences")
    finally:
        app.dependency_overrides.clear()

    assert other_user_response.status_code == 200
    assert other_user_response.json() == {
        "weekly_summary_enabled": False,
        "recipient": "other@example.com",
    }


def test_weekly_summary_dispatch_requires_scheduler_secret() -> None:
    client = TestClient(app)

    response = client.post("/emails/weekly-summary/dispatch")

    assert response.status_code == 401


def test_weekly_summary_dispatch_sends_to_opted_in_users(monkeypatch) -> None:
    session = create_test_session()
    seed_user_activity(session)
    opt_in_user(session, user_id="user-1", recipient_email="user@example.com")
    fake_sender = FakeEmailSender()
    monkeypatch.setenv("SCHEDULER_SECRET", "scheduler-secret")
    app.dependency_overrides[get_db] = override_db_session(session)
    app.dependency_overrides[get_email_sender] = lambda: fake_sender

    try:
        client = TestClient(app)
        response = client.post(
            "/emails/weekly-summary/dispatch",
            headers={"X-LeetTrack-Scheduler-Secret": "scheduler-secret"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 202
    assert response.json()["sent_count"] == 1
    assert response.json()["skipped_count"] == 0
    assert response.json()["failed_count"] == 0
    assert fake_sender.sent_messages[0]["to_email"] == "user@example.com"
    attempts = session.query(EmailDeliveryAttempt).all()
    assert len(attempts) == 1
    assert attempts[0].user_id == "user-1"
    assert attempts[0].status == "sent"
    assert attempts[0].provider_message_id == "email_test_123"


def test_weekly_summary_dispatch_skips_opted_out_users(monkeypatch) -> None:
    session = create_test_session()
    seed_user_activity(session)
    fake_sender = FakeEmailSender()
    monkeypatch.setenv("SCHEDULER_SECRET", "scheduler-secret")
    app.dependency_overrides[get_db] = override_db_session(session)
    app.dependency_overrides[get_email_sender] = lambda: fake_sender

    try:
        client = TestClient(app)
        response = client.post(
            "/emails/weekly-summary/dispatch",
            headers={"X-LeetTrack-Scheduler-Secret": "scheduler-secret"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 202
    assert response.json()["sent_count"] == 0
    assert response.json()["skipped_count"] == 0
    assert fake_sender.sent_messages == []
    assert session.query(EmailDeliveryAttempt).all() == []


def test_weekly_summary_dispatch_does_not_resend_same_week(monkeypatch) -> None:
    session = create_test_session()
    seed_user_activity(session)
    opt_in_user(session, user_id="user-1", recipient_email="user@example.com")
    fake_sender = FakeEmailSender()
    monkeypatch.setenv("SCHEDULER_SECRET", "scheduler-secret")
    app.dependency_overrides[get_db] = override_db_session(session)
    app.dependency_overrides[get_email_sender] = lambda: fake_sender

    try:
        client = TestClient(app)
        headers = {"X-LeetTrack-Scheduler-Secret": "scheduler-secret"}
        first_response = client.post("/emails/weekly-summary/dispatch", headers=headers)
        second_response = client.post("/emails/weekly-summary/dispatch", headers=headers)
    finally:
        app.dependency_overrides.clear()

    assert first_response.status_code == 202
    assert second_response.status_code == 202
    assert len(fake_sender.sent_messages) == 1
    assert second_response.json()["sent_count"] == 0
    assert second_response.json()["skipped_count"] == 1
    attempts = session.query(EmailDeliveryAttempt).all()
    assert [attempt.status for attempt in attempts] == ["sent", "skipped"]
