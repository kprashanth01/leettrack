import os
import secrets
from collections import Counter
from datetime import datetime, time, timedelta, timezone
from html import escape

from fastapi import APIRouter, Depends, Header, HTTPException, status
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
from app.repositories import (
    EmailDeliveryAttemptRepository,
    EmailPreferenceRepository,
    ensure_utc,
)
from app.schemas import (
    EmailPreferencesResponse,
    EmailPreferencesUpdate,
    WeeklySummaryDispatchResponse,
    WeeklySummaryEmailResponse,
)

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
        current_streak, max_streak = self._calculate_streaks(active_days)
        unique_problem_count = len({problem.id for problem, _submission in submissions})

        return "\n".join(
            [
                "<!doctype html>",
                "<html>",
                "<body style=\"margin:0;background:#f4f6fb;color:#111827;font-family:Inter,Arial,sans-serif;\">",
                "<div style=\"display:none;max-height:0;overflow:hidden;color:#f4f6fb;\">Your LeetTrack weekly practice snapshot is ready.</div>",
                "<table role=\"presentation\" width=\"100%\" cellspacing=\"0\" cellpadding=\"0\" style=\"background:#f4f6fb;border-collapse:collapse;\">",
                "<tr><td align=\"center\" style=\"padding:38px 22px;\">",
                "<table role=\"presentation\" width=\"760\" cellspacing=\"0\" cellpadding=\"0\" style=\"width:100%;max-width:760px;border:1px solid #2f2f2f;border-radius:16px;background:#1f1f1f;border-collapse:separate;overflow:hidden;\">",
                "<tr><td style=\"padding:34px;background:linear-gradient(135deg,#173f25,#373016);\">",
                "<p style=\"margin:0 0 10px;color:#4ade80;font-size:12px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;\">LeetTrack Weekly Report</p>",
                "<h1 style=\"margin:0;color:#ffffff;font-size:36px;line-height:1.08;\">Your practice snapshot is ready.</h1>",
                "<p style=\"margin:14px 0 0;color:#d4d4d8;font-size:16px;line-height:1.65;max-width:620px;\">A focused view of your solved volume, consistency, difficulty mix, topic coverage, recent solves, and saved notes.</p>",
                f"<p style=\"margin:14px 0 0;color:#bbf7d0;font-size:14px;font-weight:700;\">{len(submissions)} accepted submissions in this weekly snapshot.</p>",
                "</td></tr>",
                "<tr><td style=\"padding:20px;\">",
                self._render_metric_table(
                    [
                        ("Accepted", str(len(submissions)), "accepted submissions"),
                        ("Active days", str(len(active_days)), "days with solves"),
                        ("Unique", str(unique_problem_count), "tracked problems"),
                        ("Latest streak", str(current_streak), "active-day chain"),
                        ("Best streak", str(max_streak), "longest chain"),
                        ("Notes", str(len(notes)), "recent saved notes"),
                    ]
                ),
                "</td></tr>",
                "<tr><td style=\"padding:0 20px 22px;\">",
                self._render_counter_section("Difficulty mix", difficulty_counts),
                self._render_counter_section("Top topics", topic_counts),
                self._render_focus_section(
                    submissions=submissions,
                    topic_counts=topic_counts,
                    difficulty_counts=difficulty_counts,
                ),
                self._render_recent_submissions(submissions),
                self._render_recent_notes(notes),
                "</td></tr>",
                "</table>",
                "<p style=\"margin:18px 0 0;color:#64748b;font-size:12px;text-align:center;\">Sent by LeetTrack. Your scheduled email preference can be changed in the dashboard.</p>",
                "</td></tr>",
                "</table>",
                "</body>",
                "</html>",
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
            return self._render_panel(
                title=title,
                body="<p style=\"margin:0;color:#cbd5e1;\">No data yet.</p>",
            )

        items = "".join(
            "<span style=\"display:inline-block;margin:0 8px 8px 0;border-radius:999px;"
            "background:#303030;color:#f5f5f5;padding:8px 10px;font-size:13px;"
            f"font-weight:700;\">{escape(label)} <strong style=\"color:#86efac;\">{count}</strong></span>"
            for label, count in counts.most_common(5)
        )
        return self._render_panel(title=title, body=items)

    def _render_recent_submissions(
        self,
        submissions: list[tuple[Problem, Submission]],
    ) -> str:
        if not submissions:
            return self._render_panel(
                title="Recent solves",
                body="<p style=\"margin:0;color:#cbd5e1;\">No accepted submissions synced yet.</p>",
            )

        items = "".join(
            "<li style=\"margin:0 0 10px;color:#e5e7eb;\">"
            f"<strong>{escape(problem.title)}</strong>"
            f" <span style=\"color:#94a3b8;\">({escape(submission.language)})</span>"
            "</li>"
            for problem, submission in submissions[:5]
        )
        return self._render_panel(
            title="Recent solves",
            body=f"<ul style=\"margin:0;padding-left:18px;\">{items}</ul>",
        )

    def _render_recent_notes(self, notes: list[ProblemNote]) -> str:
        if not notes:
            return self._render_panel(
                title="Recent notes",
                body="<p style=\"margin:0;color:#cbd5e1;\">No notes saved yet.</p>",
            )

        items = "".join(
            "<li style=\"margin:0 0 10px;color:#e5e7eb;\">"
            f"<strong>{escape(note.problem.title)}</strong>: {escape(note.content)}"
            "</li>"
            for note in notes
        )
        return self._render_panel(
            title="Recent notes",
            body=f"<ul style=\"margin:0;padding-left:18px;\">{items}</ul>",
        )

    def _render_focus_section(
        self,
        submissions: list[tuple[Problem, Submission]],
        topic_counts: Counter[str],
        difficulty_counts: Counter[str],
    ) -> str:
        if not submissions:
            recommendation = "Sync a few accepted submissions first so LeetTrack can identify your practice pattern."
        elif difficulty_counts.get("Hard", 0) == 0 and len(submissions) >= 5:
            recommendation = "Try adding one approachable Hard problem this week to stretch your pattern recognition."
        elif topic_counts:
            strongest_topic = topic_counts.most_common(1)[0][0]
            recommendation = (
                f"You are building momentum in {strongest_topic}. Add one adjacent topic "
                "so your practice does not become too narrow."
            )
        else:
            recommendation = "Keep syncing solved problems with metadata so topic coverage becomes more useful."

        return self._render_panel(
            title="Recommended focus",
            body=(
                "<p style=\"margin:0;color:#dbeafe;line-height:1.65;\">"
                f"{escape(recommendation)}"
                "</p>"
            ),
        )

    def _render_metric_table(self, metrics: list[tuple[str, str, str]]) -> str:
        rows = []
        for index in range(0, len(metrics), 3):
            cells = "".join(
                self._render_metric_cell(label=label, value=value, helper=helper)
                for label, value, helper in metrics[index : index + 3]
            )
            rows.append(f"<tr>{cells}</tr>")

        return (
            "<table role=\"presentation\" width=\"100%\" cellspacing=\"0\" cellpadding=\"0\" style=\"border-collapse:separate;border-spacing:10px;\">"
            f"{''.join(rows)}"
            "</table>"
        )

    def _render_metric_cell(self, label: str, value: str, helper: str) -> str:
        return (
            "<td width=\"33.33%\" valign=\"top\" style=\"border:1px solid #333;border-radius:12px;background:#262626;padding:14px;\">"
            f"<p style=\"margin:0;color:#a3a3a3;font-size:12px;font-weight:700;\">{escape(label)}</p>"
            f"<strong style=\"display:block;margin:7px 0;color:#ffffff;font-size:30px;line-height:1;\">{escape(value)}</strong>"
            f"<span style=\"color:#a7f3d0;font-size:12px;\">{escape(helper)}</span>"
            "</td>"
        )

    def _render_panel(self, title: str, body: str) -> str:
        return (
            "<section style=\"margin:0 0 14px;border:1px solid #333;border-radius:12px;background:#262626;padding:18px;\">"
            f"<h2 style=\"margin:0 0 12px;color:#ffffff;font-size:19px;\">{escape(title)}</h2>"
            f"{body}"
            "</section>"
        )

    def _calculate_streaks(self, active_days: set) -> tuple[int, int]:
        if not active_days:
            return 0, 0

        sorted_days = sorted(active_days)
        max_streak = 1
        running_streak = 1
        streak_by_day = {sorted_days[0]: 1}

        for index in range(1, len(sorted_days)):
            previous_day = sorted_days[index - 1]
            current_day = sorted_days[index]
            if (current_day - previous_day).days == 1:
                running_streak += 1
            else:
                running_streak = 1

            streak_by_day[current_day] = running_streak
            max_streak = max(max_streak, running_streak)

        latest_streak = streak_by_day[sorted_days[-1]]
        return latest_streak, max_streak


def _preference_response(
    weekly_summary_enabled: bool,
    current_user: CurrentUser,
) -> EmailPreferencesResponse:
    return EmailPreferencesResponse(
        weekly_summary_enabled=weekly_summary_enabled,
        recipient=current_user.email,
    )


@router.get("/preferences", response_model=EmailPreferencesResponse)
def get_email_preferences(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> EmailPreferencesResponse:
    preference = EmailPreferenceRepository(db).get_or_create(
        user_id=current_user.id,
        recipient_email=current_user.email,
    )
    return _preference_response(
        weekly_summary_enabled=preference.weekly_summary_enabled,
        current_user=current_user,
    )


@router.patch("/preferences", response_model=EmailPreferencesResponse)
def update_email_preferences(
    payload: EmailPreferencesUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> EmailPreferencesResponse:
    preference = EmailPreferenceRepository(db).update_weekly_summary(
        user_id=current_user.id,
        weekly_summary_enabled=payload.weekly_summary_enabled,
        recipient_email=current_user.email,
    )
    return _preference_response(
        weekly_summary_enabled=preference.weekly_summary_enabled,
        current_user=current_user,
    )


def _weekly_period(now: datetime | None = None) -> tuple[datetime, datetime]:
    current_time = now or datetime.now(timezone.utc)
    current_time = ensure_utc(current_time)
    week_start_date = current_time.date() - timedelta(days=current_time.weekday())
    period_start = datetime.combine(
        week_start_date,
        time.min,
        tzinfo=timezone.utc,
    )
    return period_start, period_start + timedelta(days=7)


def _verify_scheduler_secret(secret_header: str | None) -> None:
    if not secret_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid scheduler secret.",
        )

    expected_secret = os.getenv("SCHEDULER_SECRET")
    if not expected_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Scheduler secret is not configured.",
        )

    if not secrets.compare_digest(secret_header, expected_secret):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid scheduler secret.",
        )


@router.post(
    "/weekly-summary/dispatch",
    response_model=WeeklySummaryDispatchResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def dispatch_weekly_summary_emails(
    scheduler_secret: str | None = Header(
        default=None,
        alias="X-LeetTrack-Scheduler-Secret",
    ),
    db: Session = Depends(get_db),
    email_sender: ResendEmailSender = Depends(get_email_sender),
) -> WeeklySummaryDispatchResponse:
    _verify_scheduler_secret(scheduler_secret)
    period_start, period_end = _weekly_period()
    preference_repository = EmailPreferenceRepository(db)
    attempt_repository = EmailDeliveryAttemptRepository(db)
    recipients = preference_repository.list_weekly_summary_recipients()

    sent_count = 0
    skipped_count = 0
    failed_count = 0
    builder = WeeklySummaryBuilder(db)

    for preference in recipients:
        recipient_email = preference.recipient_email
        if not recipient_email:
            continue

        if attempt_repository.has_sent(
            user_id=preference.user_id,
            email_type="weekly_summary",
            period_start=period_start,
        ):
            attempt_repository.record_attempt(
                user_id=preference.user_id,
                recipient_email=recipient_email,
                email_type="weekly_summary",
                status="skipped",
                period_start=period_start,
                period_end=period_end,
                error_message="Weekly summary already sent for this period.",
            )
            skipped_count += 1
            continue

        html = builder.build_html(user_id=preference.user_id)
        try:
            email_id = email_sender.send_email(
                to_email=recipient_email,
                subject="Your LeetTrack weekly summary",
                html=html,
            )
        except (EmailConfigurationError, EmailDeliveryError) as exc:
            attempt_repository.record_attempt(
                user_id=preference.user_id,
                recipient_email=recipient_email,
                email_type="weekly_summary",
                status="failed",
                period_start=period_start,
                period_end=period_end,
                error_message=str(exc),
            )
            failed_count += 1
            continue

        attempt_repository.record_attempt(
            user_id=preference.user_id,
            recipient_email=recipient_email,
            email_type="weekly_summary",
            status="sent",
            period_start=period_start,
            period_end=period_end,
            provider_message_id=email_id,
        )
        sent_count += 1

    return WeeklySummaryDispatchResponse(
        status="completed",
        sent_count=sent_count,
        skipped_count=skipped_count,
        failed_count=failed_count,
    )


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
