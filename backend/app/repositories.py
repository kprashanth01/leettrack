from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    EmailDeliveryAttempt,
    EmailPreference,
    LeetCodeAccount,
    Problem,
    ProblemNote,
    Submission,
    TrackedProblem,
)
from app.schemas import (
    LeetCodeProblemMetadata,
    LeetCodeSubmission,
    ProblemNoteResponse,
    TrackedProblemResponse,
    TrackedProblemSaveResponse,
)


class ProblemNotSyncedError(Exception):
    pass


def ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


class LeetCodeSubmissionRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def save_sync_result(
        self,
        user_id: str,
        username: str,
        submissions: list[LeetCodeSubmission],
        metadata_by_slug: dict[str, LeetCodeProblemMetadata] | None = None,
    ) -> int:
        account = self._get_or_create_account(user_id=user_id, username=username)
        account.last_synced_at = datetime.now(timezone.utc)
        metadata_by_slug = metadata_by_slug or {}

        saved_count = 0
        for submission in submissions:
            problem = self._get_or_create_problem(
                submission=submission,
                metadata=metadata_by_slug.get(submission.slug),
            )
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

    def list_submissions(self, user_id: str, username: str) -> list[LeetCodeSubmission]:
        rows = self._db.execute(
            select(Problem, Submission)
            .join(Submission, Submission.problem_id == Problem.id)
            .join(
                LeetCodeAccount,
                LeetCodeAccount.id == Submission.leetcode_account_id,
            )
            .where(
                LeetCodeAccount.user_id == user_id,
                LeetCodeAccount.username == username,
            )
            .order_by(Submission.submitted_at.desc())
        ).all()

        return [
            LeetCodeSubmission(
                title=problem.title,
                slug=problem.platform_slug,
                language=submission.language,
                submitted_at=ensure_utc(submission.submitted_at),
                source="leetcode",
                difficulty=problem.difficulty,
                topic_tags=problem.topic_tags or [],
            )
            for problem, submission in rows
        ]

    def _get_or_create_account(self, user_id: str, username: str) -> LeetCodeAccount:
        account = self._db.scalar(
            select(LeetCodeAccount).where(
                LeetCodeAccount.user_id == user_id,
                LeetCodeAccount.username == username,
            )
        )
        if account is not None:
            return account

        account = LeetCodeAccount(user_id=user_id, username=username)
        self._db.add(account)
        self._db.flush()
        return account

    def _get_or_create_problem(
        self,
        submission: LeetCodeSubmission,
        metadata: LeetCodeProblemMetadata | None,
    ) -> Problem:
        problem = self._db.scalar(
            select(Problem).where(
                Problem.platform == "leetcode",
                Problem.platform_slug == submission.slug,
            )
        )
        if problem is not None:
            self._update_problem_metadata(problem=problem, metadata=metadata)
            return problem

        problem = Problem(
            platform="leetcode",
            platform_slug=submission.slug,
            title=submission.title,
            difficulty=metadata.difficulty if metadata else None,
            topic_tags=metadata.topic_tags if metadata else [],
        )
        self._db.add(problem)
        self._db.flush()
        return problem

    def _update_problem_metadata(
        self,
        problem: Problem,
        metadata: LeetCodeProblemMetadata | None,
    ) -> None:
        if metadata is None:
            return

        problem.difficulty = metadata.difficulty
        problem.topic_tags = metadata.topic_tags

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

class ProblemNoteRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def list_notes(self, user_id: str) -> list[ProblemNoteResponse]:
        notes = self._db.scalars(
            select(ProblemNote)
            .join(Problem, Problem.id == ProblemNote.problem_id)
            .where(ProblemNote.user_id == user_id)
            .order_by(ProblemNote.updated_at.desc(), ProblemNote.id.desc())
        ).all()

        return [self._to_response(note) for note in notes]

    def create_note(
        self,
        user_id: str,
        problem_slug: str,
        content: str,
    ) -> ProblemNoteResponse:
        problem = self._get_noteable_problem(user_id=user_id, problem_slug=problem_slug)
        note = ProblemNote(user_id=user_id, problem_id=problem.id, content=content)
        self._db.add(note)
        self._db.commit()
        self._db.refresh(note)
        return self._to_response(note)

    def update_note(
        self,
        user_id: str,
        note_id: int,
        content: str,
    ) -> ProblemNoteResponse | None:
        note = self._get_owned_note(user_id=user_id, note_id=note_id)
        if note is None:
            return None

        note.content = content
        note.updated_at = datetime.now(timezone.utc)
        self._db.commit()
        self._db.refresh(note)
        return self._to_response(note)

    def delete_note(self, user_id: str, note_id: int) -> bool:
        note = self._get_owned_note(user_id=user_id, note_id=note_id)
        if note is None:
            return False

        self._db.delete(note)
        self._db.commit()
        return True

    def _get_noteable_problem(self, user_id: str, problem_slug: str) -> Problem:
        problem = self._get_synced_problem(
            user_id=user_id,
            problem_slug=problem_slug,
        )
        if problem is not None:
            return problem

        problem = self._get_tracked_problem(
            user_id=user_id,
            problem_slug=problem_slug,
        )
        if problem is None:
            raise ProblemNotSyncedError
        return problem

    def _get_synced_problem(
        self,
        user_id: str,
        problem_slug: str,
    ) -> Problem | None:
        problem = self._db.scalar(
            select(Problem)
            .join(Submission, Submission.problem_id == Problem.id)
            .join(
                LeetCodeAccount,
                LeetCodeAccount.id == Submission.leetcode_account_id,
            )
            .where(
                LeetCodeAccount.user_id == user_id,
                Problem.platform == "leetcode",
                Problem.platform_slug == problem_slug,
            )
            .limit(1)
        )
        return problem

    def _get_tracked_problem(
        self,
        user_id: str,
        problem_slug: str,
    ) -> Problem | None:
        return self._db.scalar(
            select(Problem)
            .join(TrackedProblem, TrackedProblem.problem_id == Problem.id)
            .where(
                TrackedProblem.user_id == user_id,
                Problem.platform == "leetcode",
                Problem.platform_slug == problem_slug,
            )
            .limit(1)
        )

    def _get_owned_note(self, user_id: str, note_id: int) -> ProblemNote | None:
        return self._db.scalar(
            select(ProblemNote).where(
                ProblemNote.id == note_id,
                ProblemNote.user_id == user_id,
            )
        )

    def _to_response(self, note: ProblemNote) -> ProblemNoteResponse:
        return ProblemNoteResponse(
            id=note.id,
            problem_title=note.problem.title,
            problem_slug=note.problem.platform_slug,
            difficulty=note.problem.difficulty,
            topic_tags=note.problem.topic_tags or [],
            content=note.content,
            created_at=ensure_utc(note.created_at),
            updated_at=ensure_utc(note.updated_at),
        )


class TrackedProblemRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def list_tracked_problems(self, user_id: str) -> list[TrackedProblemResponse]:
        tracked_problems = self._db.scalars(
            select(TrackedProblem)
            .join(Problem, Problem.id == TrackedProblem.problem_id)
            .where(TrackedProblem.user_id == user_id)
            .order_by(TrackedProblem.created_at.desc(), TrackedProblem.id.desc())
        ).all()

        return [self._to_response(tracked_problem) for tracked_problem in tracked_problems]

    def save_tracked_problem(
        self,
        user_id: str,
        problem_slug: str,
        problem_title: str,
        source: str = "extension",
        metadata: LeetCodeProblemMetadata | None = None,
    ) -> TrackedProblemSaveResponse:
        problem = self._get_or_create_problem(
            problem_slug=problem_slug,
            problem_title=problem_title,
            metadata=metadata,
        )
        existing = self._db.scalar(
            select(TrackedProblem).where(
                TrackedProblem.user_id == user_id,
                TrackedProblem.problem_id == problem.id,
            )
        )
        if existing is not None:
            return TrackedProblemSaveResponse(
                is_new=False,
                problem=self._to_response(existing),
            )

        tracked_problem = TrackedProblem(
            user_id=user_id,
            problem_id=problem.id,
            source=source,
        )
        self._db.add(tracked_problem)
        self._db.commit()
        self._db.refresh(tracked_problem)
        return TrackedProblemSaveResponse(
            is_new=True,
            problem=self._to_response(tracked_problem),
        )

    def _get_or_create_problem(
        self,
        problem_slug: str,
        problem_title: str,
        metadata: LeetCodeProblemMetadata | None,
    ) -> Problem:
        problem = self._db.scalar(
            select(Problem).where(
                Problem.platform == "leetcode",
                Problem.platform_slug == problem_slug,
            )
        )
        if problem is not None:
            if not problem.title:
                problem.title = problem_title
            self._apply_metadata(problem=problem, metadata=metadata)
            return problem

        problem = Problem(
            platform="leetcode",
            platform_slug=problem_slug,
            title=problem_title,
            difficulty=metadata.difficulty if metadata else None,
            topic_tags=metadata.topic_tags if metadata else [],
        )
        self._db.add(problem)
        self._db.flush()
        return problem

    def _apply_metadata(
        self,
        problem: Problem,
        metadata: LeetCodeProblemMetadata | None,
    ) -> None:
        if metadata is None:
            return

        problem.difficulty = metadata.difficulty
        problem.topic_tags = metadata.topic_tags

    def _to_response(self, tracked_problem: TrackedProblem) -> TrackedProblemResponse:
        return TrackedProblemResponse(
            id=tracked_problem.id,
            problem_title=tracked_problem.problem.title,
            problem_slug=tracked_problem.problem.platform_slug,
            difficulty=tracked_problem.problem.difficulty,
            topic_tags=tracked_problem.problem.topic_tags or [],
            source="extension",
            created_at=ensure_utc(tracked_problem.created_at),
        )


class EmailPreferenceRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_or_create(
        self,
        user_id: str,
        recipient_email: str | None = None,
    ) -> EmailPreference:
        preference = self._db.scalar(
            select(EmailPreference).where(EmailPreference.user_id == user_id)
        )
        if preference is not None:
            if recipient_email and preference.recipient_email != recipient_email:
                preference.recipient_email = recipient_email
                preference.updated_at = datetime.now(timezone.utc)
                self._db.commit()
                self._db.refresh(preference)
            return preference

        preference = EmailPreference(
            user_id=user_id,
            weekly_summary_enabled=False,
            recipient_email=recipient_email,
        )
        self._db.add(preference)
        self._db.commit()
        self._db.refresh(preference)
        return preference

    def update_weekly_summary(
        self,
        user_id: str,
        weekly_summary_enabled: bool,
        recipient_email: str | None = None,
    ) -> EmailPreference:
        preference = self.get_or_create(
            user_id=user_id,
            recipient_email=recipient_email,
        )
        preference.weekly_summary_enabled = weekly_summary_enabled
        if recipient_email:
            preference.recipient_email = recipient_email
        preference.updated_at = datetime.now(timezone.utc)
        self._db.commit()
        self._db.refresh(preference)
        return preference

    def list_weekly_summary_recipients(self) -> list[EmailPreference]:
        return list(
            self._db.scalars(
                select(EmailPreference)
                .where(
                    EmailPreference.weekly_summary_enabled.is_(True),
                    EmailPreference.recipient_email.is_not(None),
                )
                .order_by(EmailPreference.id.asc())
            ).all()
        )


class EmailDeliveryAttemptRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def has_sent(
        self,
        user_id: str,
        email_type: str,
        period_start: datetime,
    ) -> bool:
        existing_attempt = self._db.scalar(
            select(EmailDeliveryAttempt).where(
                EmailDeliveryAttempt.user_id == user_id,
                EmailDeliveryAttempt.email_type == email_type,
                EmailDeliveryAttempt.period_start == period_start,
                EmailDeliveryAttempt.status == "sent",
            )
        )
        return existing_attempt is not None

    def record_attempt(
        self,
        user_id: str,
        recipient_email: str,
        email_type: str,
        status: str,
        period_start: datetime,
        period_end: datetime,
        provider_message_id: str | None = None,
        error_message: str | None = None,
    ) -> EmailDeliveryAttempt:
        attempt = EmailDeliveryAttempt(
            user_id=user_id,
            recipient_email=recipient_email,
            email_type=email_type,
            status=status,
            period_start=period_start,
            period_end=period_end,
            provider_message_id=provider_message_id,
            error_message=error_message,
        )
        self._db.add(attempt)
        self._db.commit()
        self._db.refresh(attempt)
        return attempt
