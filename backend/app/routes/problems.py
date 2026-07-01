from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.auth import CurrentUser, get_current_user
from app.database import get_db
from app.repositories import TrackedProblemRepository
from app.schemas import (
    TrackedProblemCreate,
    TrackedProblemsResponse,
    TrackedProblemSaveResponse,
)

router = APIRouter(prefix="/problems", tags=["problems"])


def get_tracked_problem_repository(
    db: Session = Depends(get_db),
) -> TrackedProblemRepository:
    return TrackedProblemRepository(db)


@router.get("/tracked", response_model=TrackedProblemsResponse)
def list_tracked_problems(
    current_user: CurrentUser = Depends(get_current_user),
    repository: TrackedProblemRepository = Depends(get_tracked_problem_repository),
) -> TrackedProblemsResponse:
    return TrackedProblemsResponse(
        problems=repository.list_tracked_problems(user_id=current_user.id)
    )


@router.post(
    "/tracked",
    response_model=TrackedProblemSaveResponse,
    status_code=status.HTTP_201_CREATED,
)
def save_tracked_problem(
    request: TrackedProblemCreate,
    response: Response,
    current_user: CurrentUser = Depends(get_current_user),
    repository: TrackedProblemRepository = Depends(get_tracked_problem_repository),
) -> TrackedProblemSaveResponse:
    result = repository.save_tracked_problem(
        user_id=current_user.id,
        problem_slug=request.problem_slug,
        problem_title=request.problem_title,
        source=request.source,
    )
    if not result.is_new:
        response.status_code = status.HTTP_200_OK
    return result
