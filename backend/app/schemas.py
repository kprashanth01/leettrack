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
