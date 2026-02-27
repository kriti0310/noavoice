from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class AgentPromptUpdate(BaseModel):
    first_message: Optional[str] = None
    system_prompt: Optional[str] = None
    end_call_message: Optional[str] = None


class AgentPromptResponse(BaseModel):
    """
    Prompt response schema
    """
    assistant_id:UUID
    first_message: Optional[str] = None
    system_prompt: Optional[str] = None
    end_call_message: Optional[str] = None

    model_config = {
        "from_attributes": True
    }