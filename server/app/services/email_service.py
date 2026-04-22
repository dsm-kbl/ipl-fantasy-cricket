"""Email service for sending verification emails via Mailjet HTTP API."""

import logging

import httpx

from server.app.core.config import settings
from server.app.core.security import create_access_token

logger = logging.getLogger(__name__)

MAILJET_API_URL = "https://api.mailjet.com/v3.1/send"


def generate_verification_token(user_id: str) -> str:
    """Generate a JWT token for email verification (expires in 24h)."""
    from datetime import timedelta
    return create_access_token(subject=user_id, expires_delta=timedelta(hours=24))


def send_verification_email(to_email: str, username: str, token: str) -> bool:
    """Send a verification email via Mailjet HTTP API."""
    if not settings.mailjet_api_key or not settings.mailjet_secret_key:
        logger.warning("Mailjet API keys not configured — skipping verification email")
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

    try:
        response = httpx.post(
            MAILJET_API_URL,
            auth=(settings.mailjet_api_key, settings.mailjet_secret_key),
            json={
                "Messages": [
                    {
                        "From": {"Email": settings.mailjet_sender_email, "Name": "IPL Fantasy Cricket"},
                        "To": [{"Email": to_email, "Name": username}],
                        "Subject": "Verify your IPL Fantasy Cricket account",
                        "HTMLPart": html,
                    }
                ]
            },
            timeout=10.0,
        )
        if response.status_code == 200:
            data = response.json()
            status = data.get("Messages", [{}])[0].get("Status")
            if status == "success":
                logger.info("Verification email sent to %s", to_email)
                return True
            else:
                logger.error("Mailjet send failed: %s", data)
                return False
        else:
            logger.error("Mailjet API error: %s %s", response.status_code, response.text)
            return False
    except Exception as exc:
        logger.error("Failed to send verification email: %s", exc)
        return False


def send_feedback_email(username: str, user_email: str, message: str) -> bool:
    """Send a feedback email from a user to the admin."""
    if not settings.mailjet_api_key or not settings.mailjet_secret_key:
        logger.warning("Mailjet API keys not configured — skipping feedback email")
        return False

    html = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; padding: 40px 20px;">
        <div style="text-align: center; margin-bottom: 30px;">
            <span style="font-size: 48px;">🏏</span>
            <h1 style="color: #1e40af; margin: 10px 0 0;">IPL Fantasy — Feedback</h1>
        </div>
        <div style="background: #ffffff; border: 1px solid #e5e7eb; border-radius: 12px; padding: 32px;">
            <p style="color: #6b7280; font-size: 14px; margin-top: 0;"><strong>From:</strong> {username} ({user_email})</p>
            <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 16px 0;">
            <p style="color: #111827; line-height: 1.6; white-space: pre-wrap;">{message}</p>
        </div>
    </div>
    """

    try:
        response = httpx.post(
            MAILJET_API_URL,
            auth=(settings.mailjet_api_key, settings.mailjet_secret_key),
            json={
                "Messages": [
                    {
                        "From": {"Email": settings.mailjet_sender_email, "Name": "IPL Fantasy Feedback"},
                        "To": [{"Email": settings.feedback_recipient_email, "Name": "Admin"}],
                        "ReplyTo": {"Email": user_email, "Name": username},
                        "Subject": f"Feedback from {username}",
                        "HTMLPart": html,
                    }
                ]
            },
            timeout=10.0,
        )
        if response.status_code == 200:
            data = response.json()
            status = data.get("Messages", [{}])[0].get("Status")
            if status == "success":
                logger.info("Feedback email sent from %s", username)
                return True
            else:
                logger.error("Mailjet feedback send failed: %s", data)
                return False
        else:
            logger.error("Mailjet API error: %s %s", response.status_code, response.text)
            return False
    except Exception as exc:
        logger.error("Failed to send feedback email: %s", exc)
        return False


def send_match_reminder_email(
    to_email: str,
    username: str,
    team_a: str,
    team_b: str,
    start_time_ist: str,
    minutes_to_start: int,
    match_id: str,
) -> bool:
    """Send a match reminder email via Mailjet HTTP API.

    Reminds the user to build their team for an upcoming match.
    """
    if not settings.mailjet_api_key or not settings.mailjet_secret_key:
        logger.warning("Mailjet API keys not configured — skipping match reminder email")
        return False

    team_builder_url = f"{settings.frontend_url}/team-builder/{match_id}"
    settings_url = f"{settings.frontend_url}/settings"
    hours_to_lockout = max(0, minutes_to_start - 60)

    plain_text = f"""Hi {username},

Your team for {team_a} vs {team_b} isn't locked in yet.

Match starts at {start_time_ist} IST. Team selection closes 1 hour before start ({hours_to_lockout} minutes from now).

Pick your XI here: {team_builder_url}

Good luck!

---
IPL Fantasy Cricket
Manage notification preferences: {settings_url}
"""

    html = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; padding: 40px 20px;">
        <div style="text-align: center; margin-bottom: 30px;">
            <span style="font-size: 48px;">🏏</span>
            <h1 style="color: #1e40af; margin: 10px 0 0;">IPL Fantasy Cricket</h1>
        </div>
        <div style="background: #ffffff; border: 1px solid #e5e7eb; border-radius: 12px; padding: 32px;">
            <h2 style="color: #111827; margin-top: 0;">Hi {username},</h2>
            <p style="color: #374151; line-height: 1.6; font-size: 15px;">
                Your team for <strong>{team_a} vs {team_b}</strong> isn't locked in yet.
            </p>
            <p style="color: #374151; line-height: 1.6; font-size: 15px;">
                Match starts at <strong>{start_time_ist} IST</strong>. Team selection closes 1 hour before start — that's about {hours_to_lockout} minutes from now.
            </p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{team_builder_url}" style="background: #2563eb; color: white; padding: 14px 36px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 15px; display: inline-block;">
                    Pick Your XI
                </a>
            </div>
            <p style="color: #6b7280; line-height: 1.5; font-size: 13px; text-align: center; margin-top: 24px;">
                Good luck!
            </p>
        </div>
        <p style="text-align: center; color: #9ca3af; font-size: 12px; margin-top: 20px;">
            You're receiving this because you have a verified IPL Fantasy Cricket account.<br>
            <a href="{settings_url}" style="color: #6b7280;">Manage notification preferences</a>
        </p>
    </div>
    """

    try:
        response = httpx.post(
            MAILJET_API_URL,
            auth=(settings.mailjet_api_key, settings.mailjet_secret_key),
            json={
                "Messages": [
                    {
                        "From": {"Email": settings.mailjet_sender_email, "Name": "IPL Fantasy Cricket"},
                        "To": [{"Email": to_email, "Name": username}],
                        "ReplyTo": {"Email": settings.feedback_recipient_email, "Name": "IPL Fantasy"},
                        "Subject": f"Build your team for {team_a} vs {team_b}",
                        "TextPart": plain_text,
                        "HTMLPart": html,
                        "Headers": {
                            "List-Unsubscribe": f"<{settings_url}>",
                            "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
                        },
                    }
                ]
            },
            timeout=10.0,
        )
        if response.status_code == 200:
            data = response.json()
            status = data.get("Messages", [{}])[0].get("Status")
            if status == "success":
                logger.info("Match reminder email sent to %s (%s min)", to_email, minutes_to_start)
                return True
            logger.error("Mailjet reminder send failed: %s", data)
            return False
        logger.error("Mailjet API error: %s %s", response.status_code, response.text)
        return False
    except Exception as exc:
        logger.error("Failed to send match reminder email: %s", exc)
        return False
