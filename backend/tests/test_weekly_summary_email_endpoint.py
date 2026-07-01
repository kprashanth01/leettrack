from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.auth import CurrentUser, get_current_user
from app.database import get_db
from app.main import app
from app.models import Base
from app.repositories import LeetCodeSubmissionRepository, ProblemNoteRepository
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
    assert "2 accepted submissions" in sent_message["html"]
    assert "Two Sum" in sent_message["html"]
    assert "Remember complement lookup." in sent_message["html"]


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
