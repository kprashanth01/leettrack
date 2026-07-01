from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class HealthResponse(BaseModel):
    status: str
    service: str


class LeetCodeSyncRequest(BaseModel):
    username: str = Field(
        min_length=1,
        max_length=30,
        pattern=r"^[A-Za-z0-9_-]+$",
        description="LeetCode username to sync.",
    )
    limit: int = Field(
        default=20,
        ge=1,
        le=50,
        description="Maximum number of recent accepted submissions to fetch.",
    )

    @field_validator("username", mode="before")
    @classmethod
    def trim_username(cls, value: str) -> str:
        if isinstance(value, str):
            return value.strip()
        return value


class LeetCodeSubmission(BaseModel):
    title: str
    slug: str
    language: str
    submitted_at: datetime
    source: Literal["leetcode"] = "leetcode"
    difficulty: str | None = None
    topic_tags: list[str] = Field(default_factory=list)


class LeetCodeProblemMetadata(BaseModel):
    slug: str
    difficulty: str | None = None
    topic_tags: list[str] = Field(default_factory=list)


class LeetCodeSyncResponse(BaseModel):
    status: Literal["completed"]
    username: str
    fetched_count: int
    saved_count: int
    submissions: list[LeetCodeSubmission]


class LeetCodeSyncResult(BaseModel):
    username: str
    fetched_count: int
    saved_count: int
    submissions: list[LeetCodeSubmission]


class LeetCodeSubmissionsResponse(BaseModel):
    username: str
    submissions: list[LeetCodeSubmission]


class ProblemNoteCreate(BaseModel):
    problem_slug: str = Field(
        min_length=1,
        max_length=255,
        pattern=r"^[a-z0-9-]+$",
        description="LeetCode problem slug that already exists in synced data.",
    )
    content: str = Field(
        min_length=1,
        max_length=5000,
        description="User-authored note content for the synced problem.",
    )

    @field_validator("problem_slug", mode="before")
    @classmethod
    def trim_problem_slug(cls, value: str) -> str:
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("content", mode="before")
    @classmethod
    def trim_content(cls, value: str) -> str:
        if isinstance(value, str):
            return value.strip()
        return value


class ProblemNoteUpdate(BaseModel):
    content: str = Field(
        min_length=1,
        max_length=5000,
        description="Updated note content.",
    )

    @field_validator("content", mode="before")
    @classmethod
    def trim_content(cls, value: str) -> str:
        if isinstance(value, str):
            return value.strip()
        return value


class ProblemNoteResponse(BaseModel):
    id: int
    problem_title: str
    problem_slug: str
    difficulty: str | None = None
    topic_tags: list[str] = Field(default_factory=list)
    content: str
    created_at: datetime
    updated_at: datetime


class ProblemNotesResponse(BaseModel):
    notes: list[ProblemNoteResponse]


class TrackedProblemCreate(BaseModel):
    problem_slug: str = Field(
        min_length=1,
        max_length=255,
        pattern=r"^[a-z0-9-]+$",
        description="LeetCode problem slug detected by the extension.",
    )
    problem_title: str = Field(
        min_length=1,
        max_length=255,
        description="LeetCode problem title detected by the extension.",
    )
    source: Literal["extension"] = "extension"

    @field_validator("problem_slug", mode="before")
    @classmethod
    def trim_problem_slug(cls, value: str) -> str:
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("problem_title", mode="before")
    @classmethod
    def trim_problem_title(cls, value: str) -> str:
        if isinstance(value, str):
            return value.strip()
        return value


class TrackedProblemResponse(BaseModel):
    id: int
    problem_title: str
    problem_slug: str
    difficulty: str | None = None
    topic_tags: list[str] = Field(default_factory=list)
    source: Literal["extension"] = "extension"
    created_at: datetime


class TrackedProblemSaveResponse(BaseModel):
    is_new: bool
    problem: TrackedProblemResponse


class TrackedProblemsResponse(BaseModel):
    problems: list[TrackedProblemResponse]
