from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_cors_allowed_origins, validate_runtime_configuration
from app.routes.account import router as account_router
from app.routes.emails import router as emails_router
from app.routes.leetcode import router as leetcode_router
from app.routes.notes import router as notes_router
from app.routes.problems import router as problems_router
from app.schemas import HealthResponse

validate_runtime_configuration()

app = FastAPI(
    title="LeetTrack API",
    description="Backend API for the LeetTrack competitive programming tracker.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(leetcode_router)
app.include_router(notes_router)
app.include_router(problems_router)
app.include_router(emails_router)
app.include_router(account_router)


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health_check() -> HealthResponse:
    return HealthResponse(status="ok", service="leettrack-api")
