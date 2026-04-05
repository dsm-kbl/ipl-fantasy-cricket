"""Authentication API routes."""

import asyncio

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from server.app.core.database import get_db
from server.app.core.deps import get_current_user
from server.app.core.security import create_access_token, verify_access_token
from server.app.models.user import User
from server.app.schemas.auth import (
    AuthTokenResponse,
    LoginRequest,
    RegisterRequest,
    UserOut,
)
from server.app.services.auth_service import AuthError
from server.app.services import auth_service
from server.app.services.email_service import generate_verification_token, send_verification_email

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", status_code=201)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register a new user account and send verification email."""
    try:
        user_out = await auth_service.register(
            db, username=body.username, email=body.email, password=body.password
        )
        await db.commit()

        # Send verification email in the background so the response isn't blocked
        token = generate_verification_token(str(user_out.id))
        asyncio.get_event_loop().run_in_executor(
            None, send_verification_email, body.email, body.username, token
        )

        return {"message": "Account created. Please check your email to verify your account."}
    except AuthError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.error_response.model_dump(),
        )


@router.get("/verify-email")
async def verify_email(token: str = Query(...), db: AsyncSession = Depends(get_db)):
    """Verify a user's email address using the token from the verification email."""
    subject = verify_access_token(token)
    if not subject:
        raise HTTPException(status_code=400, detail={"error": {"code": "INVALID_TOKEN", "message": "Invalid or expired verification link", "details": []}})

    import uuid
    try:
        user_id = uuid.UUID(subject)
    except ValueError:
        raise HTTPException(status_code=400, detail={"error": {"code": "INVALID_TOKEN", "message": "Invalid verification link", "details": []}})

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail={"error": {"code": "NOT_FOUND", "message": "User not found", "details": []}})

    if user.is_verified:
        return {"message": "Email already verified", "verified": True}

    user.is_verified = True
    await db.commit()
    return {"message": "Email verified successfully", "verified": True}


@router.post("/resend-verification")
async def resend_verification(body: dict, db: AsyncSession = Depends(get_db)):
    """Resend the verification email. Accepts {"email": "..."} — no auth required."""
    email = body.get("email", "").strip().lower()
    if not email:
        raise HTTPException(status_code=400, detail={"error": {"code": "VALIDATION_ERROR", "message": "Email is required", "details": []}})

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()

    # Always return success to avoid leaking whether an email exists
    if not user or user.is_verified:
        return {"message": "If that email is registered and unverified, a new verification link has been sent."}

    token = generate_verification_token(str(user.id))
    asyncio.get_event_loop().run_in_executor(
        None, send_verification_email, user.email, user.username, token
    )

    return {"message": "If that email is registered and unverified, a new verification link has been sent."}


@router.post("/login", response_model=AuthTokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate a user and return a JWT token."""
    try:
        return await auth_service.login(db, email=body.email, password=body.password)
    except AuthError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.error_response.model_dump(),
        )


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Log out the current user."""
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(get_current_user)):
    """Return the currently authenticated user."""
    return UserOut.model_validate(current_user)
