# app/repository/booking_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional
from app.models.calcom_model import Booking


class BookingRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_name_phone(self, name: str, phone: str) -> Optional[Booking]:
        result = await self.db.execute(
            select(Booking).where(
                and_(
                    Booking.name == name,
                    Booking.phone == phone,
                    Booking.is_deleted == False,
                    Booking.status == "booked"
                )
            ).order_by(Booking.created_at.desc())
        )
        return result.scalars().first()

    async def get_by_booking_id(self, booking_id: str) -> Optional[Booking]:
        result = await self.db.execute(
            select(Booking).where(
                Booking.booking_id == booking_id,
                Booking.is_deleted == False,
            )
        )
        return result.scalars().first()

    async def save(self, data: dict) -> Booking:
        booking = Booking(**data)
        self.db.add(booking)
        await self.db.commit()
        await self.db.refresh(booking)
        return booking

    async def update_status(
        self,
        booking_id: str,
        status: str,
        reason: Optional[str] = None,
    ) -> Optional[Booking]:
        booking = await self.get_by_booking_id(booking_id)
        if not booking:
            return None

        booking.status = status
        if reason:
            booking.cancel_reason = reason

        await self.db.commit()
        await self.db.refresh(booking)
        return booking