"""Cron-triggered routes for scheduled tasks.

Protected by a shared secret in the X-Cron-Secret header. Designed to be
called by external schedulers like cron-job.org.
"""

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from server.app.core.config import settings
from server.app.core.database import get_db
from server.app.services.notification_service import send_pending_match_reminders

router = APIRouter(prefix="/api/cron", tags=["cron"])


def _verify_secret(x_cron_secret: str | None = Header(None)) -> None:
    """Verify the shared secret in the X-Cron-Secret header."""
    if not x_cron_secret or x_cron_secret != settings.cron_secret:
        raise HTTPException(status_code=403, detail={"error": {"code": "FORBIDDEN", "message": "Invalid cron secret", "details": []}})


@router.post("/send-match-reminders")
async def send_match_reminders(
    _auth: None = Depends(_verify_secret),
    db: AsyncSession = Depends(get_db),
):
    """Trigger sending of match reminder emails to users without a team.

    Meant to be called every 15 minutes by an external scheduler.
    """
    stats = await send_pending_match_reminders(db)
    return {"status": "ok", "stats": stats}
