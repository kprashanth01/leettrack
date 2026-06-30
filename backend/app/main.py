from fastapi import FastAPI

from app.routes.leetcode import router as leetcode_router
from app.schemas import HealthResponse

app = FastAPI(
    title="LeetTrack API",
    description="Backend API for the LeetTrack competitive programming tracker.",
    version="0.1.0",
)

app.include_router(leetcode_router)


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health_check() -> HealthResponse:
    return HealthResponse(status="ok", service="leettrack-api")
