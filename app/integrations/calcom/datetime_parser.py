from datetime import datetime,timezone,timedelta
from typing import List
import pytz
import dateutil.parser


def parse_user_datetime(date_str: str, time_str: str) -> str:
    """
    Accepts human-friendly date/time like:
    20 Feb 2026 , 2:00 PM
    20 february 2026 14:00
    2026-02-20 14:00
    """

    try:
        dt_string = f"{date_str} {time_str}"
        dt = dateutil.parser.parse(dt_string)

        ist = pytz.timezone("Asia/Kolkata")
        if not dt.tzinfo:
            dt = ist.localize(dt)

        return dt.astimezone(pytz.utc).isoformat()

    except Exception:
        raise ValueError(f"Invalid date/time format: {dt_string}")
    
def get_today_iso():
    """
    Return today's start time in ISO format (UTC)
    Example: 2026-02-09T00:00:00Z
    """
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    return today.strftime("%Y-%m-%dT%H:%M:%SZ")


def get_90_days_iso():
    """
    Return date after 90 days in ISO UTC
    """
    future = datetime.now(timezone.utc) + timedelta(days=90)
    return future.strftime("%Y-%m-%dT%H:%M:%SZ")