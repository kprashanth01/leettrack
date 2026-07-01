from app.leetcode_client import LeetCodeClientError, LeetCodeGraphQLClient
from app.repositories import LeetCodeSubmissionRepository
from app.schemas import LeetCodeProblemMetadata, LeetCodeSubmission, LeetCodeSyncResult


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
        fetched_count = len(submissions)
        metadata_by_slug = self._fetch_metadata_by_slug(submissions)
        saved_count = 0
        if self._repository is not None:
            saved_count = self._repository.save_sync_result(
                user_id=user_id,
                username=username,
                submissions=submissions,
                metadata_by_slug=metadata_by_slug,
            )
            submissions = self._repository.list_submissions(
                user_id=user_id,
                username=username,
            )

        return LeetCodeSyncResult(
            username=username,
            fetched_count=fetched_count,
            saved_count=saved_count,
            submissions=submissions,
        )

    def _fetch_metadata_by_slug(
        self,
        submissions: list[LeetCodeSubmission],
    ) -> dict[str, LeetCodeProblemMetadata]:
        metadata_by_slug: dict[str, LeetCodeProblemMetadata] = {}

        if not hasattr(self._client, "fetch_problem_metadata"):
            return metadata_by_slug

        for slug in {submission.slug for submission in submissions}:
            try:
                metadata = self._client.fetch_problem_metadata(slug)
            except LeetCodeClientError:
                continue

            if metadata is not None:
                metadata_by_slug[slug] = metadata

        return metadata_by_slug
