import uuid
from sqlalchemy import Column, String, Date, Time, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from app.config.database import Base


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name = Column(String)
    email = Column(String)
    phone = Column(String)

    purpose = Column(Text)

    appointment_date = Column(Date)
    appointment_time = Column(Time)

    booking_uid = Column(String, unique=True)

    status = Column(String)

    rescheduled_from = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)