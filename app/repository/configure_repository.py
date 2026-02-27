from sqlalchemy.future import select
from app.models.agent_model import Agent
from uuid import UUID


class ConfigureRepository:

    def __init__(self, db):
        self.db = db

    async def get_agent(self, agent_id:UUID):

        result = await self.db.execute(
            select(Agent).where(
                Agent.id == agent_id,
                Agent.is_deleted == False
            )
        )
        return result.scalar_one_or_none()

    async def save_configuration(self, agent, config_data: dict):

        voice = config_data.get("voice", {})
        settings = config_data.get("settings", {})

        # Language
        agent.language = voice.get("language")

        # Voice
        agent.voice_provider = voice.get("provider", "elevenlabs")
        agent.voice_id = voice.get("voice_id")
        agent.voice_name = voice.get("voice_name")

        # Voice options
        agent.multi_lingual = voice.get("multi_lingual", False)
        agent.voice_recording_enabled = settings.get("recording_enabled", False)

        # Advanced ElevenLabs settings (if added later)
        agent.voice_stability = voice.get("voice_stability")
        agent.voice_similarity_boost = voice.get("voice_similarity_boost")
        agent.voice_style = voice.get("voice_style")

        # Test message
        agent.test_message = config_data.get("test_message")

        self.db.add(agent)
        await self.db.commit()
        await self.db.refresh(agent)

        return agent