from sqlalchemy import Column,String, Text, DateTime, ForeignKey , Boolean
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.models.base import Base
from sqlalchemy import Column

class Agent(Base):
    __tablename__ = "noavoice_agents"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Owner of agent
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True  )

    # Basic info
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    #prompt
    first_message = Column(Text, nullable=True)
    end_call_message = Column(Text, nullable=True)
    system_prompt = Column(Text, nullable=True)

    #Configure agents
     # Language selected in configure UI
    language = Column(String, nullable=True)

    # Voice provider (elevenlabs, openai, azure etc)
    voice_provider = Column(String, default="elevenlabs")

    # ElevenLabs voice id
    voice_id = Column(String, nullable=True)

    # Voice display name
    voice_name = Column(String, nullable=True)

    # Multi-lingual toggle
    multi_lingual = Column(Boolean, default=False , server_default="false", nullable=False)

    # Custom voice (if user pastes ElevenLabs ID)
    is_custom_voice = Column(Boolean, default=False)

    # Voice recording enabled
    voice_recording_enabled = Column(Boolean, default=False)

    # Voice stability (ElevenLabs advanced)
    voice_stability = Column(String, nullable=True)

    # Voice similarity boost
    voice_similarity_boost = Column(String, nullable=True)

    # Voice style
    voice_style = Column(String, nullable=True)

    # Test message text used in preview
    test_message = Column(Text, nullable=True)

    # Agent published
    is_published = Column(Boolean, default=False)
    
    is_deleted = Column(Boolean, default=False)

    is_template = Column(Boolean, default=False)
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    timezone = Column(String,default="UTC",server_default="UTC",nullable=False)
