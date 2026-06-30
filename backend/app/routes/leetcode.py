from fastapi import APIRouter, Depends, HTTPException, status

from app.leetcode_client import LeetCodeClientError
from app.schemas import LeetCodeSyncRequest, LeetCodeSyncResponse
from app.services import LeetCodeSyncService

router = APIRouter(prefix="/leetcode", tags=["leetcode"])


def get_leetcode_sync_service() -> LeetCodeSyncService:
    return LeetCodeSyncService()


@router.post("/sync", response_model=LeetCodeSyncResponse)
def sync_recent_accepted_submissions(
    request: LeetCodeSyncRequest,
    service: LeetCodeSyncService = Depends(get_leetcode_sync_service),
) -> LeetCodeSyncResponse:
    try:
        submissions = service.sync_recent_accepted_submissions(
            username=request.username,
            limit=request.limit,
        )
    except LeetCodeClientError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not sync with LeetCode. Please try again later.",
        ) from exc

    return LeetCodeSyncResponse(
        status="completed",
        username=request.username,
        fetched_count=len(submissions),
        submissions=submissions,
    )
