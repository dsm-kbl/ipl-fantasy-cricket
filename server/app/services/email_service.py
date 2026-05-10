"""Email service using Gmail SMTP for better deliverability."""

import logging
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr, make_msgid

from server.app.core.config import settings
from server.app.core.security import create_access_token

logger = logging.getLogger(__name__)


def generate_verification_token(user_id: str) -> str:
    """Generate a JWT token for email verification (expires in 24h)."""
    from datetime import timedelta
    return create_access_token(subject=user_id, expires_delta=timedelta(hours=24))


def _send_smtp(
    to_email: str,
    to_name: str,
    subject: str,
    html_body: str,
    text_body: str,
    reply_to: str | None = None,
    extra_headers: dict[str, str] | None = None,
) -> bool:
    """Send an email via Gmail SMTP. Returns True on success."""
    if not settings.smtp_user or not settings.smtp_password:
        logger.warning("Gmail SMTP not configured — skipping email")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = formataddr((settings.smtp_sender_name, settings.smtp_sender_email))
    msg["To"] = formataddr((to_name, to_email))
    msg["Message-ID"] = make_msgid(domain=settings.smtp_sender_email.split("@")[-1])
    if reply_to:
        msg["Reply-To"] = reply_to
    if extra_headers:
        for key, value in extra_headers.items():
            msg[key] = value

    msg.attach(MIMEText(text_body, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as server:
            server.starttls(context=context)
            server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(msg)
        logger.info("Email sent to %s (subject: %s)", to_email, subject)
        return True
    except Exception as exc:
        logger.error("Failed to send email to %s: %s", to_email, exc)
        return False


def send_verification_email(to_email: str, username: str, token: str) -> bool:
    """Send a verification email via Gmail SMTP."""
    verify_url = f"{settings.frontend_url}/verify-email?token={token}"

    text_body = f"""Hi {username},

Welcome to IPL Fantasy Cricket 2026!

Please verify your email address by clicking the link below:
{verify_url}

This link expires in 24 hours. If you didn't create this account, you can safely ignore this email.

---
IPL Fantasy Cricket
"""

    html_body = f"""
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
                <a href="{verify_url}" style="background: #2563eb; color: white; padding: 12px 32px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 14px; display: inline-block;">
                    Verify Email Address
                </a>
            </div>
            <p style="color: #9ca3af; font-size: 13px; line-height: 1.5;">
                This link expires in 24 hours. If you didn't create this account, you can safely ignore this email.
            </p>
        </div>
    </div>
    """

    return _send_smtp(
        to_email=to_email,
        to_name=username,
        subject="Verify your IPL Fantasy Cricket account",
        html_body=html_body,
        text_body=text_body,
    )


def send_feedback_email(username: str, user_email: str, message: str) -> bool:
    """Send a feedback email from a user to the admin."""
    text_body = f"""Feedback from {username} ({user_email}):

{message}
"""

    html_body = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; padding: 40px 20px;">
        <div style="background: #ffffff; border: 1px solid #e5e7eb; border-radius: 12px; padding: 32px;">
            <p style="color: #6b7280; font-size: 14px; margin-top: 0;"><strong>From:</strong> {username} ({user_email})</p>
            <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 16px 0;">
            <p style="color: #111827; line-height: 1.6; white-space: pre-wrap;">{message}</p>
        </div>
    </div>
    """

    return _send_smtp(
        to_email=settings.feedback_recipient_email,
        to_name="Admin",
        subject=f"Feedback from {username}",
        html_body=html_body,
        text_body=text_body,
        reply_to=user_email,
    )


def send_match_reminder_email(
    to_email: str,
    username: str,
    team_a: str,
    team_b: str,
    start_time_ist: str,
    minutes_to_start: int,
    match_id: str,
) -> bool:
    """Send a match reminder email via Gmail SMTP."""
    team_builder_url = f"{settings.frontend_url}/team-builder/{match_id}"
    settings_url = f"{settings.frontend_url}/settings"
    hours_to_lockout = max(0, minutes_to_start - 60)

    text_body = f"""Hi {username},

Your team for {team_a} vs {team_b} isn't locked in yet.

Match starts at {start_time_ist} IST. Team selection closes 1 hour before start ({hours_to_lockout} minutes from now).

Pick your XI here: {team_builder_url}

Good luck!

---
IPL Fantasy Cricket
Manage notification preferences: {settings_url}
"""

    html_body = f"""
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

    return _send_smtp(
        to_email=to_email,
        to_name=username,
        subject=f"Build your team for {team_a} vs {team_b}",
        html_body=html_body,
        text_body=text_body,
        reply_to=settings.feedback_recipient_email,
        extra_headers={
            "List-Unsubscribe": f"<{settings_url}>",
            "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
        },
    )
