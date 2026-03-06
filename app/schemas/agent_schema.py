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
    
class CreateAgentData(BaseModel):
    agent: AgentResponse
    class Config:
        from_attributes = True

class AssistantResponse(BaseModel):
    id: UUID
    company_id: UUID

    name: str
    description: Optional[str]

    system_prompt: Optional[str]

    language: Optional[str]
    voice: Optional[str]

    multi_lingual_enabled: bool

    first_message: Optional[str]
    first_message_mode: str

    end_call_message: Optional[str]
    end_call_function_enabled: bool

    recording_enabled: bool

    voicemail_message: Optional[str] = None
    summary_email: Optional[str] = None
    forwarding_number: Optional[str] = None

    actions: List[str] = []

    hipaa_enabled: bool = False

    timezone: str

    providers: List[str] = []

    created_at: datetime

    file_ids: List[UUID] = []

    detect_caller_number: bool

    class Config:
        from_attributes = True
class SingleAgentData(BaseModel):
    assistant: AssistantResponse

    class Config:
        from_attributes = True 
class AgentListItem(BaseModel):
    id: UUID
    company_id: UUID
    name: str
    description: Optional[str]
    language: Optional[str]
    voice: Optional[str]
    multi_lingual_enabled: bool
    created_at: datetime
    detect_caller_number: bool
    calls: int
    average_call_duration: float
class AgentListData(BaseModel):
    assistants: List[AgentListItem]
    class Config:
        from_attributes = True
