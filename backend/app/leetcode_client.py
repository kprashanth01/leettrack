from datetime import datetime, timezone
from typing import Any

import httpx

from app.schemas import LeetCodeProblemMetadata, LeetCodeSubmission


RECENT_ACCEPTED_SUBMISSIONS_QUERY = """
query recentAcSubmissions($username: String!, $limit: Int!) {
  recentAcSubmissionList(username: $username, limit: $limit) {
    title
    titleSlug
    timestamp
    statusDisplay
    lang
  }
}
"""

PROBLEM_METADATA_QUERY = """
query questionData($titleSlug: String!) {
  question(titleSlug: $titleSlug) {
    difficulty
    topicTags {
      name
    }
  }
}
"""


class LeetCodeClientError(Exception):
    """Raised when LeetCode cannot return usable submission data."""


class LeetCodeGraphQLClient:
    def __init__(
        self,
        http_client: httpx.Client | None = None,
        endpoint: str = "https://leetcode.com/graphql",
    ) -> None:
        self._endpoint = endpoint
        self._http_client = http_client or httpx.Client(
            timeout=10.0,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "LeetTrack/0.1",
                "Referer": "https://leetcode.com/",
            },
        )

    def fetch_recent_accepted_submissions(
        self,
        username: str,
        limit: int,
    ) -> list[LeetCodeSubmission]:
        payload = {
            "query": RECENT_ACCEPTED_SUBMISSIONS_QUERY,
            "variables": {"username": username, "limit": limit},
        }

        try:
            response = self._http_client.post(self._endpoint, json=payload)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise LeetCodeClientError("LeetCode request failed") from exc

        try:
            body = response.json()
        except ValueError as exc:
            raise LeetCodeClientError("LeetCode returned invalid JSON") from exc
        if body.get("errors"):
            message = body["errors"][0].get("message", "LeetCode returned an error")
            raise LeetCodeClientError(message)

        raw_submissions = body.get("data", {}).get("recentAcSubmissionList")
        if raw_submissions is None:
            raise LeetCodeClientError("LeetCode response did not include submissions")

        return [self._to_submission(item) for item in raw_submissions]

    def fetch_problem_metadata(self, slug: str) -> LeetCodeProblemMetadata | None:
        payload = {
            "query": PROBLEM_METADATA_QUERY,
            "variables": {"titleSlug": slug},
        }

        try:
            response = self._http_client.post(self._endpoint, json=payload)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise LeetCodeClientError("LeetCode metadata request failed") from exc

        try:
            body = response.json()
        except ValueError as exc:
            raise LeetCodeClientError("LeetCode returned invalid metadata JSON") from exc
        if body.get("errors"):
            message = body["errors"][0].get("message", "LeetCode returned an error")
            raise LeetCodeClientError(message)

        raw_question = body.get("data", {}).get("question")
        if raw_question is None:
            return None

        return LeetCodeProblemMetadata(
            slug=slug,
            difficulty=raw_question.get("difficulty"),
            topic_tags=[
                tag["name"]
                for tag in raw_question.get("topicTags", [])
                if isinstance(tag.get("name"), str)
            ],
        )

    def _to_submission(self, item: dict[str, Any]) -> LeetCodeSubmission:
        timestamp = int(item["timestamp"])
        return LeetCodeSubmission(
            title=item["title"],
            slug=item["titleSlug"],
            language=item["lang"],
            submitted_at=datetime.fromtimestamp(timestamp, tz=timezone.utc),
            source="leetcode",
        )
