from app.leetcode_client import LeetCodeGraphQLClient
from app.repositories import LeetCodeSubmissionRepository
from app.schemas import LeetCodeSyncResult


class LeetCodeSyncService:
    def __init__(
        self,
        client: LeetCodeGraphQLClient | None = None,
        repository: LeetCodeSubmissionRepository | None = None,
    ) -> None:
        self._client = client or LeetCodeGraphQLClient()
        self._repository = repository

    def sync_recent_accepted_submissions(
        self,
        user_id: str,
        username: str,
        limit: int,
    ) -> LeetCodeSyncResult:
        submissions = self._client.fetch_recent_accepted_submissions(
            username=username,
            limit=limit,
        )
        saved_count = 0
        if self._repository is not None:
            saved_count = self._repository.save_sync_result(
                user_id=user_id,
                username=username,
                submissions=submissions,
            )

        return LeetCodeSyncResult(
            username=username,
            fetched_count=len(submissions),
            saved_count=saved_count,
            submissions=submissions,
        )
