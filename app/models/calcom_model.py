import uuid
import enum
from sqlalchemy import Column, String, DateTime, Integer, Text, Enum
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from app.config.database import Base


class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    calcom_booking_id = Column(Integer)
    booking_uid = Column(String, unique=True)

    name = Column(String)
    email = Column(String)
    phone = Column(String)

    timezone = Column(String)

    start_time = Column(DateTime)
    end_time = Column(DateTime)

    event_type_id = Column(Integer)
    duration_minutes = Column(Integer)

    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING)

    notes = Column(Text)


    cancellation_reason = Column(Text)
    rescheduling_reason = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)