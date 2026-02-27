from sqlalchemy import Column, ForeignKey
from app.models.base import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid
class AgentKnowledge(Base):
    __tablename__ = "agent_knowledge"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    agent_id = Column(UUID(as_uuid=True), ForeignKey("noavoice_agents.id"))
    knowledge_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_bases.id"))
