from pydantic import BaseModel
from typing import Optional,List
from datetime import datetime
from uuid import UUID
class AgentCreate(BaseModel):
    name: str
    description: Optional[str] = None

class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class AgentResponse(BaseModel):
    id: UUID
    user_id: Optional[UUID]

    name: str
    description: Optional[str]

    first_message: Optional[str]
    end_call_message: Optional[str]
    system_prompt: Optional[str]

    language: Optional[str]

    voice_provider: Optional[str]
    voice_id: Optional[str]
    voice_name: Optional[str]

    multi_lingual: bool
    is_custom_voice: Optional[bool]
    voice_recording_enabled: Optional[bool]

    voice_stability: Optional[str]
    voice_similarity_boost: Optional[str]
    voice_style: Optional[str]

    test_message: Optional[str]

    is_published: Optional[bool]
    is_deleted: Optional[bool]
    is_template: Optional[bool]

    created_at: datetime
    timezone: str

    class Config:
        from_attributes = True

    class Config:
        from_attributes = True
class SingleAgentData(BaseModel):
    assistant: AgentResponse

    class Config:
        from_attributes = True 
class AgentListData(BaseModel):
    assistants: List[AgentResponse]
    class Config:
        from_attributes = True
