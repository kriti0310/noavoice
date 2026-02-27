from sqlalchemy import Column,ForeignKey, Text, DateTime
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from app.models.base import Base 
import uuid
from sqlalchemy.dialects.postgresql import UUID

class KnowledgeBase(Base):
    __tablename__ = "knowledge_bases"   

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False) 

    file_id = Column(UUID(as_uuid=True), ForeignKey("files.id"), nullable=False)

    # each chunk stored as a row
    content = Column(Text, nullable=False)

    # pgvector embedding
    embedding = Column(Vector(1536))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
