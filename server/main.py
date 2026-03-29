"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from server.app.core.config import settings
from server.app.core.exceptions import AppError
from server.app.routes import admin, auth, dashboard, fantasy_teams, leaderboard, matches

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle hook."""
    logger.info("IPL Fantasy Cricket API starting up")
    yield


app = FastAPI(
    title="IPL Fantasy Cricket",
    description="IPL Fantasy Cricket API",
    version="0.1.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Global exception handlers
# ---------------------------------------------------------------------------

@app.exception_handler(AppError)
async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
    """Map any custom AppError subclass to the standard error envelope."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(
    _request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Convert FastAPI/Pydantic 422 errors into the standard error envelope."""
    details = []
    for err in exc.errors():
        field = ".".join(str(loc) for loc in err.get("loc", []) if loc != "body")
        details.append({"field": field or None, "message": err.get("msg", "Invalid value")})
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Validation failed",
                "details": details,
            }
        },
    )


@app.exception_handler(IntegrityError)
async def integrity_error_handler(
    _request: Request, exc: IntegrityError
) -> JSONResponse:
    """Map database constraint violations to 409 CONFLICT."""
    logger.warning("Database integrity error: %s", exc)
    return JSONResponse(
        status_code=409,
        content={
            "error": {
                "code": "CONFLICT",
                "message": "A resource with the given data already exists",
                "details": [],
            }
        },
    )


@app.exception_handler(Exception)
async def unhandled_error_handler(_request: Request, exc: Exception) -> JSONResponse:
    """Catch-all for unexpected errors — returns 500 INTERNAL_ERROR."""
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": [],
            }
        },
    )


# ---------------------------------------------------------------------------
# Middleware & routers
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(matches.router)
app.include_router(admin.router)
app.include_router(fantasy_teams.router)
app.include_router(leaderboard.router)
app.include_router(dashboard.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
