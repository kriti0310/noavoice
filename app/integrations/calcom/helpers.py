from livekit.agents.llm import function_tool
from livekit.agents import RunContext
from datetime import datetime, timezone
from typing import Optional
import pytz
import logging

from app.integrations.calcom_client import CalComClient, CalComAPIError
from app.repository.booking_repository import BookingRepository
from datetime_parser import parse_user_datetime
from app.config.settings import settings

logger = logging.getLogger(__name__)

# ─── Constants ────────────────────────────────────────────────────────────────

IST = pytz.timezone("Asia/Kolkata")
SLOT_MATCH_TOLERANCE_SECONDS = 120


# ─── Helpers ──────────────────────────────────────────────────────────────────

def get_cal() -> CalComClient:
    return CalComClient()


def to_ist_readable(utc_str: str) -> str:
    utc_dt = datetime.fromisoformat(utc_str.replace("Z", "+00:00"))
    return utc_dt.astimezone(IST).strftime("%d %b %Y %I:%M %p")


def to_utc_iso(iso_time: str) -> str:
    return datetime.fromisoformat(iso_time).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def extract_booking_uid(res: dict) -> Optional[str]:
    return (
        res.get("uid")
        or res.get("data", {}).get("uid")
        or res.get("data", {}).get("booking", {}).get("uid")
    )


# NOTE: db (AsyncSession) must be injected into context by your LiveKit session setup
# Access it via: context.userdata.db

# ─── Tools ────────────────────────────────────────────────────────────────────

@function_tool()
async def check_availability(
    context: RunContext,
    date: str,
    time: str,
) -> str:
    """
    Check if a time slot is available on the given date.
    Suggests up to 5 alternatives if not available.

    Args:
        date: Date (e.g. "tomorrow", "2024-08-13")
        time: Time (e.g. "3pm", "15:00")
    """
    try:
        cal      = get_cal()
        iso_time = parse_user_datetime(date, time)
        target   = datetime.fromisoformat(iso_time).astimezone()
        date_str = target.strftime("%Y-%m-%d")

        slots = await cal.get_available_slots(
            start_date=date_str,
            end_date=date_str,
        )

        if not slots:
            return f"❌ No slots available on {date}. Please choose another day."

        available_times = []
        for slot in slots:
            slot_dt = datetime.fromisoformat(slot)
            if abs((slot_dt - target).total_seconds()) <= SLOT_MATCH_TOLERANCE_SECONDS:
                return "✅ Slot is available for booking."
            available_times.append(slot_dt.astimezone(IST).strftime("%I:%M %p"))

        suggestions = "\n• ".join(available_times[:5])
        return (
            f"❌ Requested time is not available on {date}.\n\n"
            f"Available slots:\n• {suggestions}"
        )

    except Exception as e:
        logger.error(f"check_availability error: {e}")
        return f"⚠️ Error checking availability: {str(e)}"


@function_tool()
async def book_meeting(
    context: RunContext,
    date: str,
    time: str,
    name: str,
    email: str,
    phone: str,
    purpose: str,
) -> str:
    """
    Book an appointment on Cal.com and save to PostgreSQL.

    Args:
        date:    Date (e.g. "2024-08-13")
        time:    Time (e.g. "3pm")
        name:    Patient full name
        email:   Patient email
        phone:   Patient phone number
        purpose: Reason for appointment
    """
    db   = context.userdata.db
    repo = BookingRepository(db)

    try:
        # ── Duplicate check ───────────────────────────────────────
        existing = await repo.get_by_name_phone(name, phone)
        if existing:
            if existing.appointment_date == date and existing.appointment_time == time:
                return (
                    f"✅ Your appointment is already confirmed!\n\n"
                    f"📅 Date: {date}\n"
                    f"🕐 Time: {time}\n"
                    f"📋 Purpose: {existing.purpose or purpose}\n\n"
                    f"See you at the clinic!"
                )

        # ── Create on Cal.com ─────────────────────────────────────
        cal        = get_cal()
        iso_time   = parse_user_datetime(date, time)
        res        = await cal.create_booking(start=iso_time, name=name, email=email, phone=phone)
        booking_id = extract_booking_uid(res)

        logger.info(f"Cal.com create_booking response: {res}")

        if not booking_id:
            logger.warning(f"No UID in Cal.com response: {res}")
            return "⚠️ Booking attempted but no confirmation ID returned. Please try again."

        # ── Save to PostgreSQL ─────────────────────────────────────
        await repo.save({
            "booking_id":       booking_id,
            "name":             name,
            "email":            email,
            "phone":            phone,
            "purpose":          purpose,
            "appointment_date": date,
            "appointment_time": time,
            "status":           "booked",
            "created_at":       datetime.utcnow(),
        })

        return (
            f"✅ Appointment booked successfully!\n\n"
            f"👤 Name:       {name}\n"
            f"📧 Email:      {email}\n"
            f"📞 Phone:      {phone}\n"
            f"📅 Date:       {date}\n"
            f"🕐 Time:       {time}\n"
            f"📋 Purpose:    {purpose}\n"
            f"🔖 Booking ID: {booking_id}\n\n"
            f"A confirmation email will be sent. See you at the clinic!"
        )

    except CalComAPIError as e:
        error_msg = str(e)
        logger.warning(f"CalComAPIError in book_meeting: {error_msg}")

        if "already has booking" in error_msg or "not available" in error_msg:
            existing = await repo.get_by_name_phone(name, phone)
            if existing:
                return (
                    f"✅ You already have a confirmed appointment!\n\n"
                    f"📅 Date: {existing.appointment_date}\n"
                    f"🕐 Time: {existing.appointment_time}\n"
                    f"📋 Purpose: {existing.purpose or purpose}"
                )
            return f"❌ This time slot is no longer available. Shall I check other times for {date}?"

        logger.error(f"Cal.com booking failed: {error_msg}")
        return "❌ Booking failed. Please try again or choose a different time."

    except Exception as e:
        logger.exception(f"Unexpected error in book_meeting: {e}")
        return "⚠️ An unexpected error occurred. Please try again."


@function_tool()
async def get_booking_details(
    context: RunContext,
    name: str,
    phone: str,
) -> str:
    """
    Fetch appointment details using patient name and phone.

    Args:
        name:  Patient full name
        phone: Patient phone number
    """
    db   = context.userdata.db
    repo = BookingRepository(db)

    try:
        booking = await repo.get_by_name_phone(name, phone)
        if not booking:
            return "❌ No booking found with this name and phone number."

        cal          = get_cal()
        booking_data = await cal.get_booking(booking.booking_id)
        data         = booking_data.get("data", {})
        start_time   = data.get("startTime") or data.get("start")

        if not start_time:
            return "❌ Could not read appointment time from the system."

        return f"📅 Your appointment is scheduled on {to_ist_readable(start_time)}."

    except Exception as e:
        logger.exception(f"get_booking_details error: {e}")
        return "⚠️ Unable to fetch booking details right now. Please try again."


@function_tool()
async def reschedule_meeting(
    context: RunContext,
    name: str,
    phone: str,
    new_date: str,
    new_time: str,
    reason: Optional[str] = None,
) -> str:
    """
    Reschedule an existing appointment to a new date and time.

    Args:
        name:     Patient full name
        phone:    Patient phone number
        new_date: New date (e.g. "2024-08-15")
        new_time: New time (e.g. "10am")
        reason:   Optional reason for rescheduling
    """
    db   = context.userdata.db
    repo = BookingRepository(db)

    try:
        booking = await repo.get_by_name_phone(name, phone)
        if not booking:
            return "❌ No booking found with this name and phone number."

        cal      = get_cal()
        iso_time = to_utc_iso(parse_user_datetime(new_date, new_time))

        res     = await cal.reschedule_booking(
            booking_uid=booking.booking_id,
            new_start=iso_time,
            reason=reason or "Patient requested reschedule",
        )
        new_uid = extract_booking_uid(res)

        # ── Update old booking ─────────────────────────────────────
        await repo.update_status(
            booking.booking_id,
            status="rescheduled",
            reason="rescheduled_by_patient",
        )

        # ── Save new booking ───────────────────────────────────────
        if new_uid:
            await repo.save({
                "booking_id":        new_uid,
                "name":              name,
                "email":             booking.email,
                "phone":             phone,
                "purpose":           booking.purpose,
                "appointment_date":  new_date,
                "appointment_time":  new_time,
                "status":            "booked",
                "rescheduled_from":  booking.booking_id,
                "created_at":        datetime.utcnow(),
            })

        return (
            f"🔄 Appointment rescheduled successfully!\n\n"
            f"📅 New Date:    {new_date}\n"
            f"🕐 New Time:    {new_time}\n"
            f"🔖 New Booking ID: {new_uid or 'N/A'}"
        )

    except CalComAPIError as e:
        logger.error(f"CalComAPIError in reschedule_meeting: {e}")
        return "❌ Rescheduling failed. Please try again or contact the clinic."

    except Exception as e:
        logger.exception(f"Unexpected error in reschedule_meeting: {e}")
        return "⚠️ Unable to reschedule. Please try again."


@function_tool()
async def cancel_meeting(
    context: RunContext,
    name: str,
    phone: str,
    reason: Optional[str] = None,
) -> str:
    """
    Cancel an existing appointment using patient name and phone.

    Args:
        name:   Patient full name
        phone:  Patient phone number
        reason: Optional cancellation reason
    """
    db         = context.userdata.db
    repo       = BookingRepository(db)
    booking_id = None

    try:
        booking = await repo.get_by_name_phone(name, phone)
        if not booking:
            return "❌ No booking found with this name and phone number."

        if booking.status == "cancelled":
            return "ℹ️ This appointment is already cancelled."

        booking_id = booking.booking_id
        cal        = get_cal()

        await cal.cancel_booking(
            booking_uid=booking_id,
            reason=reason or "Cancelled by patient",
        )

        await repo.update_status(
            booking_id,
            status="cancelled",
            reason=reason or "cancelled_by_patient",
        )

        return "✅ Your appointment has been cancelled successfully."

    except CalComAPIError as e:
        error_msg = str(e).lower()
        logger.warning(f"CalComAPIError in cancel_meeting: {e}")

        if "already" in error_msg:
            if booking_id:
                await repo.update_status(
                    booking_id,
                    status="cancelled",
                    reason="already_cancelled_on_cal",
                )
            return "ℹ️ This appointment was already cancelled."

        if "not found" in error_msg:
            return "⚠️ Booking not found on the calendar system."

        return "❌ Cancellation failed. Please contact the clinic directly."

    except Exception as e:
        logger.exception(f"Unexpected error in cancel_meeting: {e}")
        return "⚠️ Unable to cancel appointment. Please try again."