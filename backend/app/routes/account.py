from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import CurrentUser, get_current_user
from app.database import get_db
from app.repositories import LeetCodeSubmissionRepository
from app.schemas import AccountSettingsResponse

router = APIRouter(prefix="/account", tags=["account"])


@router.get("/settings", response_model=AccountSettingsResponse)
def get_account_settings(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AccountSettingsResponse:
    account = LeetCodeSubmissionRepository(db).get_latest_account_for_user(
        user_id=current_user.id,
    )

    return AccountSettingsResponse(
        leetcode_username=account.username if account is not None else None,
        email=current_user.email,
    )
