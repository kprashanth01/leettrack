from datetime import datetime, timezone

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.models import Base, LeetCodeAccount, Problem, Submission
from app.repositories import LeetCodeSubmissionRepository
from app.schemas import LeetCodeProblemMetadata, LeetCodeSubmission
from app.services import LeetCodeSyncService


class FakeLeetCodeClient:
    def fetch_recent_accepted_submissions(
        self, username: str, limit: int
    ) -> list[LeetCodeSubmission]:
        return [
            LeetCodeSubmission(
                title="Two Sum",
                slug="two-sum",
                language="python3",
                submitted_at=datetime(2026, 7, 1, 12, 0, tzinfo=timezone.utc),
            ),
            LeetCodeSubmission(
                title="Valid Parentheses",
                slug="valid-parentheses",
                language="cpp",
                submitted_at=datetime(2026, 7, 2, 12, 0, tzinfo=timezone.utc),
            ),
        ]

    def fetch_problem_metadata(self, slug: str) -> LeetCodeProblemMetadata | None:
        metadata_by_slug = {
            "two-sum": LeetCodeProblemMetadata(
                slug="two-sum",
                difficulty="Easy",
                topic_tags=["Array", "Hash Table"],
            ),
            "valid-parentheses": LeetCodeProblemMetadata(
                slug="valid-parentheses",
                difficulty="Easy",
                topic_tags=["Stack", "String"],
            ),
        }
        return metadata_by_slug.get(slug)


def create_test_session() -> Session:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    return Session(engine)


def test_sync_persists_leetcode_account_problems_and_submissions() -> None:
    session = create_test_session()
    service = LeetCodeSyncService(
        client=FakeLeetCodeClient(),
        repository=LeetCodeSubmissionRepository(session),
    )

    result = service.sync_recent_accepted_submissions(
        user_id="user-1",
        username="kprashanth01",
        limit=10,
    )

    account = session.scalar(
        select(LeetCodeAccount).where(
            LeetCodeAccount.user_id == "user-1",
            LeetCodeAccount.username == "kprashanth01",
        )
    )
    problems = session.scalars(select(Problem)).all()
    submissions = session.scalars(select(Submission)).all()

    assert result.fetched_count == 2
    assert result.saved_count == 2
    assert account is not None
    assert account.last_synced_at is not None
    assert {problem.platform_slug for problem in problems} == {
        "two-sum",
        "valid-parentheses",
    }
    assert {
        (problem.platform_slug, problem.difficulty, tuple(problem.topic_tags))
        for problem in problems
    } == {
        ("two-sum", "Easy", ("Array", "Hash Table")),
        ("valid-parentheses", "Easy", ("Stack", "String")),
    }
    assert len(submissions) == 2


def test_sync_does_not_duplicate_existing_submissions() -> None:
    session = create_test_session()
    service = LeetCodeSyncService(
        client=FakeLeetCodeClient(),
        repository=LeetCodeSubmissionRepository(session),
    )

    first_result = service.sync_recent_accepted_submissions(
        user_id="user-1",
        username="kprashanth01",
        limit=10,
    )
    second_result = service.sync_recent_accepted_submissions(
        user_id="user-1",
        username="kprashanth01",
        limit=10,
    )

    submissions = session.scalars(select(Submission)).all()

    assert first_result.saved_count == 2
    assert second_result.fetched_count == 2
    assert second_result.saved_count == 0
    assert len(submissions) == 2


def test_repository_lists_saved_submissions_for_username_newest_first() -> None:
    session = create_test_session()
    repository = LeetCodeSubmissionRepository(session)
    fake_client = FakeLeetCodeClient()
    submissions = fake_client.fetch_recent_accepted_submissions(
        username="kprashanth01",
        limit=10,
    )
    repository.save_sync_result(
        user_id="user-1",
        username="kprashanth01",
        submissions=submissions,
        metadata_by_slug={
            submission.slug: fake_client.fetch_problem_metadata(submission.slug)
            for submission in submissions
            if fake_client.fetch_problem_metadata(submission.slug) is not None
        },
    )

    saved_submissions = repository.list_submissions(
        user_id="user-1",
        username="kprashanth01",
    )

    assert [submission.title for submission in saved_submissions] == [
        "Valid Parentheses",
        "Two Sum",
    ]
    assert saved_submissions[0].slug == "valid-parentheses"
    assert saved_submissions[0].language == "cpp"
    assert saved_submissions[0].difficulty == "Easy"
    assert saved_submissions[0].topic_tags == ["Stack", "String"]


def test_repository_isolates_submissions_by_user_id() -> None:
    session = create_test_session()
    repository = LeetCodeSubmissionRepository(session)
    submissions = FakeLeetCodeClient().fetch_recent_accepted_submissions(
        username="kprashanth01",
        limit=10,
    )

    repository.save_sync_result(
        user_id="user-1",
        username="kprashanth01",
        submissions=submissions,
    )
    repository.save_sync_result(
        user_id="user-2",
        username="kprashanth01",
        submissions=submissions,
    )

    assert (
        len(
            repository.list_submissions(
                user_id="user-1",
                username="kprashanth01",
            )
        )
        == 2
    )
    assert (
        len(
            repository.list_submissions(
                user_id="user-2",
                username="kprashanth01",
            )
        )
        == 2
    )
