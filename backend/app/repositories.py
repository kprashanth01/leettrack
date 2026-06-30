from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import LeetCodeAccount, Problem, Submission
from app.schemas import LeetCodeSubmission


class LeetCodeSubmissionRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def save_sync_result(
        self,
        username: str,
        submissions: list[LeetCodeSubmission],
    ) -> int:
        account = self._get_or_create_account(username)
        account.last_synced_at = datetime.now(timezone.utc)

        saved_count = 0
        for submission in submissions:
            problem = self._get_or_create_problem(submission)
            if self._submission_exists(account.id, problem.id, submission.submitted_at):
                continue

            self._db.add(
                Submission(
                    leetcode_account_id=account.id,
                    problem_id=problem.id,
                    submitted_at=submission.submitted_at,
                    language=submission.language,
                    status="accepted",
                )
            )
            saved_count += 1

        self._db.commit()
        return saved_count

    def list_submissions(self, username: str) -> list[LeetCodeSubmission]:
        rows = self._db.execute(
            select(Problem, Submission)
            .join(Submission, Submission.problem_id == Problem.id)
            .join(
                LeetCodeAccount,
                LeetCodeAccount.id == Submission.leetcode_account_id,
            )
            .where(LeetCodeAccount.username == username)
            .order_by(Submission.submitted_at.desc())
        ).all()

        return [
            LeetCodeSubmission(
                title=problem.title,
                slug=problem.platform_slug,
                language=submission.language,
                submitted_at=self._ensure_utc(submission.submitted_at),
                source="leetcode",
            )
            for problem, submission in rows
        ]

    def _get_or_create_account(self, username: str) -> LeetCodeAccount:
        account = self._db.scalar(
            select(LeetCodeAccount).where(LeetCodeAccount.username == username)
        )
        if account is not None:
            return account

        account = LeetCodeAccount(username=username)
        self._db.add(account)
        self._db.flush()
        return account

    def _get_or_create_problem(self, submission: LeetCodeSubmission) -> Problem:
        problem = self._db.scalar(
            select(Problem).where(
                Problem.platform == "leetcode",
                Problem.platform_slug == submission.slug,
            )
        )
        if problem is not None:
            return problem

        problem = Problem(
            platform="leetcode",
            platform_slug=submission.slug,
            title=submission.title,
        )
        self._db.add(problem)
        self._db.flush()
        return problem

    def _submission_exists(
        self,
        account_id: int,
        problem_id: int,
        submitted_at: datetime,
    ) -> bool:
        existing_submission = self._db.scalar(
            select(Submission).where(
                Submission.leetcode_account_id == account_id,
                Submission.problem_id == problem_id,
                Submission.submitted_at == submitted_at,
            )
        )
        return existing_submission is not None

    def _ensure_utc(self, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
