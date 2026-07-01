from collections import Counter
from html import escape

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import CurrentUser, get_current_user
from app.database import get_db
from app.email_service import (
    EmailConfigurationError,
    EmailDeliveryError,
    ResendEmailSender,
)
from app.models import LeetCodeAccount, Problem, ProblemNote, Submission
from app.repositories import ensure_utc
from app.schemas import WeeklySummaryEmailResponse

router = APIRouter(prefix="/emails", tags=["emails"])


def get_email_sender() -> ResendEmailSender:
    return ResendEmailSender()


class WeeklySummaryBuilder:
    def __init__(self, db: Session) -> None:
        self._db = db

    def build_html(self, user_id: str) -> str:
        submissions = self._list_submissions(user_id=user_id)
        notes = self._list_recent_notes(user_id=user_id)
        topic_counts = Counter(
            tag
            for problem, _submission in submissions
            for tag in (problem.topic_tags or [])
        )
        difficulty_counts = Counter(
            problem.difficulty or "Unknown" for problem, _submission in submissions
        )
        active_days = {
            ensure_utc(submission.submitted_at).date()
            for _problem, submission in submissions
        }

        return "\n".join(
            [
                "<h1>Your LeetTrack weekly summary</h1>",
                "<p>Here is your current practice snapshot from LeetTrack.</p>",
                "<h2>Progress</h2>",
                "<ul>",
                f"<li>{len(submissions)} accepted submissions</li>",
                f"<li>{len(active_days)} active days recorded</li>",
                f"<li>{len({problem.id for problem, _submission in submissions})} unique problems</li>",
                "</ul>",
                self._render_counter_section("Difficulty mix", difficulty_counts),
                self._render_counter_section("Top topics", topic_counts),
                self._render_recent_submissions(submissions),
                self._render_recent_notes(notes),
            ]
        )

    def _list_submissions(self, user_id: str) -> list[tuple[Problem, Submission]]:
        return self._db.execute(
            select(Problem, Submission)
            .join(Submission, Submission.problem_id == Problem.id)
            .join(
                LeetCodeAccount,
                LeetCodeAccount.id == Submission.leetcode_account_id,
            )
            .where(LeetCodeAccount.user_id == user_id)
            .order_by(Submission.submitted_at.desc())
        ).all()

    def _list_recent_notes(self, user_id: str) -> list[ProblemNote]:
        return list(
            self._db.scalars(
                select(ProblemNote)
                .join(Problem, Problem.id == ProblemNote.problem_id)
                .where(ProblemNote.user_id == user_id)
                .order_by(ProblemNote.updated_at.desc(), ProblemNote.id.desc())
                .limit(3)
            ).all()
        )

    def _render_counter_section(self, title: str, counts: Counter[str]) -> str:
        if not counts:
            return f"<h2>{escape(title)}</h2><p>No data yet.</p>"

        items = "".join(
            f"<li>{escape(label)}: {count}</li>"
            for label, count in counts.most_common(5)
        )
        return f"<h2>{escape(title)}</h2><ul>{items}</ul>"

    def _render_recent_submissions(
        self,
        submissions: list[tuple[Problem, Submission]],
    ) -> str:
        if not submissions:
            return "<h2>Recent solves</h2><p>No accepted submissions synced yet.</p>"

        items = "".join(
            f"<li>{escape(problem.title)} ({escape(submission.language)})</li>"
            for problem, submission in submissions[:5]
        )
        return f"<h2>Recent solves</h2><ul>{items}</ul>"

    def _render_recent_notes(self, notes: list[ProblemNote]) -> str:
        if not notes:
            return "<h2>Recent notes</h2><p>No notes saved yet.</p>"

        items = "".join(
            f"<li><strong>{escape(note.problem.title)}</strong>: {escape(note.content)}</li>"
            for note in notes
        )
        return f"<h2>Recent notes</h2><ul>{items}</ul>"


@router.post(
    "/weekly-summary",
    response_model=WeeklySummaryEmailResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def send_weekly_summary_email(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
    email_sender: ResendEmailSender = Depends(get_email_sender),
) -> WeeklySummaryEmailResponse:
    html = WeeklySummaryBuilder(db).build_html(user_id=current_user.id)

    try:
        email_id = email_sender.send_email(
            to_email=current_user.email,
            subject="Your LeetTrack weekly summary",
            html=html,
        )
    except EmailConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Email sending is not configured.",
        ) from exc
    except EmailDeliveryError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Email provider could not send the summary.",
        ) from exc

    return WeeklySummaryEmailResponse(
        status="sent",
        email_id=email_id,
        recipient=current_user.email,
    )
