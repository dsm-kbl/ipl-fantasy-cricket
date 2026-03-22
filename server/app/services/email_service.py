"""Email service for sending verification emails via Gmail SMTP."""

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from server.app.core.config import settings
from server.app.core.security import create_access_token

logger = logging.getLogger(__name__)


def generate_verification_token(user_id: str) -> str:
    """Generate a JWT token for email verification (expires in 24h)."""
    from datetime import timedelta
    return create_access_token(subject=user_id, expires_delta=timedelta(hours=24))


def send_verification_email(to_email: str, username: str, token: str) -> bool:
    """Send a verification email with a clickable link."""
    if not settings.smtp_user or not settings.smtp_password:
        logger.warning("SMTP not configured — skipping verification email")
        return False

    verify_url = f"{settings.frontend_url}/verify-email?token={token}"

    html = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; padding: 40px 20px;">
        <div style="text-align: center; margin-bottom: 30px;">
            <span style="font-size: 48px;">🏏</span>
            <h1 style="color: #1e40af; margin: 10px 0 0;">IPL Fantasy Cricket</h1>
        </div>
        <div style="background: #ffffff; border: 1px solid #e5e7eb; border-radius: 12px; padding: 32px;">
            <h2 style="color: #111827; margin-top: 0;">Welcome, {username}!</h2>
            <p style="color: #6b7280; line-height: 1.6;">
                Thanks for signing up for IPL Fantasy Cricket 2026. Please verify your email address to activate your account and start building your dream XI.
            </p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{verify_url}" style="background: linear-gradient(to right, #2563eb, #4f46e5); color: white; padding: 12px 32px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 14px; display: inline-block;">
                    Verify Email Address
                </a>
            </div>
            <p style="color: #9ca3af; font-size: 13px; line-height: 1.5;">
                This link expires in 24 hours. If you didn't create this account, you can safely ignore this email.
            </p>
        </div>
        <p style="text-align: center; color: #9ca3af; font-size: 12px; margin-top: 20px;">
            IPL Fantasy Cricket 2026 — Build. Compete. Win.
        </p>
    </div>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Verify your IPL Fantasy Cricket account"
    msg["From"] = f"IPL Fantasy Cricket <{settings.smtp_user}>"
    msg["To"] = to_email
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.sendmail(settings.smtp_user, to_email, msg.as_string())
        logger.info("Verification email sent to %s", to_email)
        return True
    except Exception as exc:
        logger.error("Failed to send verification email: %s", exc)
        return False
