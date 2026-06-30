from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.leetcode_client import LeetCodeClientError
from app.repositories import LeetCodeSubmissionRepository
from app.schemas import (
    LeetCodeSubmissionsResponse,
    LeetCodeSyncRequest,
    LeetCodeSyncResponse,
)
from app.services import LeetCodeSyncService

router = APIRouter(prefix="/leetcode", tags=["leetcode"])


def get_leetcode_sync_service(db: Session = Depends(get_db)) -> LeetCodeSyncService:
    return LeetCodeSyncService(repository=LeetCodeSubmissionRepository(db))


def get_leetcode_submission_repository(
    db: Session = Depends(get_db),
) -> LeetCodeSubmissionRepository:
    return LeetCodeSubmissionRepository(db)


@router.post("/sync", response_model=LeetCodeSyncResponse)
def sync_recent_accepted_submissions(
    request: LeetCodeSyncRequest,
    service: LeetCodeSyncService = Depends(get_leetcode_sync_service),
) -> LeetCodeSyncResponse:
    try:
        result = service.sync_recent_accepted_submissions(
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
        username=result.username,
        fetched_count=result.fetched_count,
        saved_count=result.saved_count,
        submissions=result.submissions,
    )


@router.get("/submissions", response_model=LeetCodeSubmissionsResponse)
def list_submissions(
    request: LeetCodeSyncRequest = Depends(),
    repository: LeetCodeSubmissionRepository = Depends(
        get_leetcode_submission_repository
    ),
) -> LeetCodeSubmissionsResponse:
    return LeetCodeSubmissionsResponse(
        username=request.username,
        submissions=repository.list_submissions(username=request.username),
    )
