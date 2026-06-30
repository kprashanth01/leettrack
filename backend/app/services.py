from app.leetcode_client import LeetCodeGraphQLClient
from app.schemas import LeetCodeSubmission


class LeetCodeSyncService:
    def __init__(self, client: LeetCodeGraphQLClient | None = None) -> None:
        self._client = client or LeetCodeGraphQLClient()

    def sync_recent_accepted_submissions(
        self,
        username: str,
        limit: int,
    ) -> list[LeetCodeSubmission]:
        return self._client.fetch_recent_accepted_submissions(
            username=username,
            limit=limit,
        )
