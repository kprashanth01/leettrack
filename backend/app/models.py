from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class LeetCodeAccount(Base):
    __tablename__ = "leetcode_accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(30), unique=True, index=True)
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
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    submissions: Mapped[list["Submission"]] = relationship(back_populates="problem")


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
