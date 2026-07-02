from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class LeetCodeAccount(Base):
    __tablename__ = "leetcode_accounts"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "username",
            name="uq_leetcode_accounts_user_username",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str | None] = mapped_column(String(255), index=True)
    username: Mapped[str] = mapped_column(String(30), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    submissions: Mapped[list["Submission"]] = relationship(
        back_populates="leetcode_account"
    )


class Problem(Base):
    __tablename__ = "problems"
    __table_args__ = (
        UniqueConstraint(
            "platform",
            "platform_slug",
            name="uq_problems_platform_slug",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    platform: Mapped[str] = mapped_column(String(30), index=True)
    platform_slug: Mapped[str] = mapped_column(String(255), index=True)
    title: Mapped[str] = mapped_column(String(255))
    difficulty: Mapped[str | None] = mapped_column(String(20))
    topic_tags: Mapped[list[str]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    submissions: Mapped[list["Submission"]] = relationship(back_populates="problem")
    notes: Mapped[list["ProblemNote"]] = relationship(back_populates="problem")
    tracked_by_users: Mapped[list["TrackedProblem"]] = relationship(
        back_populates="problem"
    )


class Submission(Base):
    __tablename__ = "submissions"
    __table_args__ = (
        UniqueConstraint(
            "leetcode_account_id",
            "problem_id",
            "submitted_at",
            name="uq_submissions_account_problem_submitted_at",
        ),
        Index("ix_submissions_account_submitted_at", "leetcode_account_id", "submitted_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    leetcode_account_id: Mapped[int] = mapped_column(
        ForeignKey("leetcode_accounts.id", ondelete="CASCADE"),
        index=True,
    )
    problem_id: Mapped[int] = mapped_column(
        ForeignKey("problems.id", ondelete="CASCADE"),
        index=True,
    )
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    language: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(30), default="accepted")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    leetcode_account: Mapped[LeetCodeAccount] = relationship(
        back_populates="submissions"
    )
    problem: Mapped[Problem] = relationship(back_populates="submissions")


class ProblemNote(Base):
    __tablename__ = "problem_notes"
    __table_args__ = (
        Index("ix_problem_notes_user_updated_at", "user_id", "updated_at"),
        Index("ix_problem_notes_user_problem", "user_id", "problem_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(String(255), index=True)
    problem_id: Mapped[int] = mapped_column(
        ForeignKey("problems.id", ondelete="CASCADE"),
        index=True,
    )
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )

    problem: Mapped[Problem] = relationship(back_populates="notes")


class TrackedProblem(Base):
    __tablename__ = "tracked_problems"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "problem_id",
            name="uq_tracked_problems_user_problem",
        ),
        Index("ix_tracked_problems_user_created_at", "user_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(String(255), index=True)
    problem_id: Mapped[int] = mapped_column(
        ForeignKey("problems.id", ondelete="CASCADE"),
        index=True,
    )
    source: Mapped[str] = mapped_column(String(30), default="extension")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    problem: Mapped[Problem] = relationship(back_populates="tracked_by_users")


class EmailPreference(Base):
    __tablename__ = "email_preferences"
    __table_args__ = (
        UniqueConstraint("user_id", name="uq_email_preferences_user_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(String(255), index=True)
    weekly_summary_enabled: Mapped[bool] = mapped_column(Boolean(), default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )
