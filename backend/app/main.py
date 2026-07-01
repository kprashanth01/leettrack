import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.leetcode import router as leetcode_router
from app.routes.notes import router as notes_router
from app.routes.problems import router as problems_router
from app.schemas import HealthResponse

app = FastAPI(
    title="LeetTrack API",
    description="Backend API for the LeetTrack competitive programming tracker.",
    version="0.1.0",
)

allowed_origins = os.getenv(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174,http://localhost:5175,http://127.0.0.1:5175,http://localhost:5176,http://127.0.0.1:5176",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in allowed_origins if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(leetcode_router)
app.include_router(notes_router)
app.include_router(problems_router)


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health_check() -> HealthResponse:
    return HealthResponse(status="ok", service="leettrack-api")
