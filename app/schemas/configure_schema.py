from pydantic import BaseModel
from typing import Optional


class VoiceSettings(BaseModel):
    provider: str = "elevenlabs"
    voice_id: str
    voice_name: Optional[str]
    language: str
    multi_lingual: bool = False


class AdditionalSettings(BaseModel):
    recording_enabled: bool = False


class ConfigureAgentRequest(BaseModel):
    voice: VoiceSettings
    settings: AdditionalSettings


class ConfigureAgentResponse(BaseModel):
    message: str