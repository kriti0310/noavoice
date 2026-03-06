from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
import logging

from app.tools.tool import (
    get_available_slots,
    book_appointment,
    get_booking,
    reschedule_appointment,
    cancel_appointment,
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Cal.com Appointments"])


class SlotsRequest(BaseModel):
    date: str
    timezone: str = "Asia/Kolkata"

class BookingRequest(BaseModel):
    start: str
    name: str
    email: str
    phone: Optional[str] = None
    timezone: str = "Asia/Kolkata"
    notes: Optional[str] = None
    session_id: Optional[str] = None

class GetBookingRequest(BaseModel):
    booking_uid: Optional[str] = None
    email: Optional[str] = None

class RescheduleRequest(BaseModel):
    booking_uid: str
    new_start: str
    reason: Optional[str] = None

class CancelRequest(BaseModel):
    booking_uid: str
    reason: Optional[str] = None


@router.get("/health")
async def health():
    return {"status": "ok"}

@router.post("/slots")
async def slots(req: SlotsRequest):
    result = await get_available_slots(date=req.date, timezone=req.timezone)
    return {"result": result}

@router.post("/book")
async def book(req: BookingRequest):
    result = await book_appointment(
        start=req.start, name=req.name, email=req.email,
        phone=req.phone, timezone=req.timezone,
        notes=req.notes, session_id=req.session_id,
    )
    return {"result": result}

@router.post("/booking")
async def get_booking_endpoint(req: GetBookingRequest):
    result = await get_booking(booking_uid=req.booking_uid, email=req.email)
    return {"result": result}

@router.post("/reschedule")
async def reschedule(req: RescheduleRequest):
    result = await reschedule_appointment(
        booking_uid=req.booking_uid, new_start=req.new_start, reason=req.reason,
    )
    return {"result": result}

@router.post("/cancel")
async def cancel(req: CancelRequest):
    result = await cancel_appointment(
        booking_uid=req.booking_uid, reason=req.reason,
    )
    return {"result": result}
