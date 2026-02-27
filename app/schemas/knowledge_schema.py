from pydantic import BaseModel, HttpUrl
from typing import Optional
from uuid import UUID

class KnowledgeUpload(BaseModel):
    agent_id: UUID

    url: Optional[HttpUrl] = None