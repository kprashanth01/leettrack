from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.auth import CurrentUser, get_current_user
from app.database import get_db
from app.repositories import ProblemNoteRepository, ProblemNotSyncedError
from app.schemas import (
    ProblemNoteCreate,
    ProblemNoteResponse,
    ProblemNotesResponse,
    ProblemNoteUpdate,
)

router = APIRouter(prefix="/notes", tags=["notes"])


def get_problem_note_repository(
    db: Session = Depends(get_db),
) -> ProblemNoteRepository:
    return ProblemNoteRepository(db)


@router.get("", response_model=ProblemNotesResponse)
def list_notes(
    current_user: CurrentUser = Depends(get_current_user),
    repository: ProblemNoteRepository = Depends(get_problem_note_repository),
) -> ProblemNotesResponse:
    return ProblemNotesResponse(notes=repository.list_notes(user_id=current_user.id))


@router.post(
    "",
    response_model=ProblemNoteResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_note(
    request: ProblemNoteCreate,
    current_user: CurrentUser = Depends(get_current_user),
    repository: ProblemNoteRepository = Depends(get_problem_note_repository),
) -> ProblemNoteResponse:
    try:
        return repository.create_note(
            user_id=current_user.id,
            problem_slug=request.problem_slug,
            content=request.content,
        )
    except ProblemNotSyncedError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sync or save this LeetCode problem before adding notes.",
        ) from exc


@router.patch("/{note_id}", response_model=ProblemNoteResponse)
def update_note(
    note_id: int,
    request: ProblemNoteUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    repository: ProblemNoteRepository = Depends(get_problem_note_repository),
) -> ProblemNoteResponse:
    note = repository.update_note(
        user_id=current_user.id,
        note_id=note_id,
        content=request.content,
    )
    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found.",
        )
    return note


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    note_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    repository: ProblemNoteRepository = Depends(get_problem_note_repository),
) -> Response:
    if not repository.delete_note(user_id=current_user.id, note_id=note_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found.",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
