from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.agent_repository import AgentRepository
from app.schemas.agent_schema import AgentCreate, AgentUpdate, AgentResponse
from app.services.retrieval_service import RetrievalService
from app.services.llm_service import LLMService
from app.config.default_prompt import DEFAULT_AGENT_PROMPT
from uuid import UUID
from app.services.default_template import load_default_template
from sqlalchemy import select
from app.models.agent_model import Agent

class AgentService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = AgentRepository(db)
        self.retrieval = RetrievalService(db)
        self.llm = LLMService()

    # ─── Agent CRUD ───────────────────────────────────────────────────────────

    async def create_agent(self, user_id: UUID, data: AgentCreate):

        defaults = load_default_template()

        agent = await self.repo.create(user_id, data)

        # PROMPT FIELDS — saved at creation
        agent.system_prompt = defaults["system_prompt"]
        agent.first_message = defaults["first_message"]
        agent.end_call_message = defaults["end_call_message"]

        # CONFIG FIELDS
        agent.language = defaults["language"]
        agent.voice_provider = defaults["voice_provider"]
        agent.voice_id = defaults["voice_id"]
        agent.voice_name = defaults["voice_name"]
        agent.multi_lingual = defaults["multi_lingual"]

        await self.db.commit()
        await self.db.refresh(agent)

        return {
            "status": True,
            "message": "",
            "data": {
                "assistant": agent
            }
        }

    async def list_agents(self, user_id: UUID):
        agents = await self.repo.get_all(user_id)

        assistants = []

        for agent in agents:
            assistants.append({
                "id": agent.id,
                "company_id": agent.user_id,
                "name": agent.name,
                "description": agent.description,
                "language": agent.language,
                "voice": agent.voice_id,
                "multi_lingual_enabled": agent.multi_lingual,
                "created_at": agent.created_at,
                "detect_caller_number": False,
                "calls": 0,
                "average_call_duration": 0
            })
        return {
            "status": True,
            "message": "",
            "data": {
                "assistants": assistants
            }
        }
    async def get_agent(self, agent_id: UUID, user_id: UUID):
        agent = await self.repo.get_by_id(agent_id, user_id)
        if not agent:
            return None

        return {
        "status": True,
        "message": "",
        "data": {
            "assistant": {
                "id": agent.id,
                "company_id": agent.user_id,
                "name": agent.name,
                "description": agent.description,
                "system_prompt": agent.system_prompt,
                "language": agent.language,
                "voice": agent.voice_id,
                "multi_lingual_enabled": agent.multi_lingual,
                "first_message": agent.first_message,
                "first_message_mode": "assistant-speaks-first",
                "end_call_message": agent.end_call_message,
                "end_call_function_enabled": False,
                "recording_enabled": agent.voice_recording_enabled,
                "voicemail_message": None,
                "summary_email": None,
                "forwarding_number": None,
                "actions": [],
                "hipaa_enabled": False,
                "timezone": agent.timezone,
                "providers": [],
                "created_at": agent.created_at,
                "file_ids": [],
                "detect_caller_number": False
            }
        }
    }

    async def update_agent(self, agent_id: UUID, user_id: UUID, data: AgentUpdate):
        agent = await self.repo.get_by_id(agent_id, user_id)

        if not agent:
            return None

        updated_agent = await self.repo.update(agent, data)

        return {
            "status": True,
            "message": "Agent updated successfully",
            "data": {
                "assistant": {
                    "id": updated_agent.id,
                    "company_id": updated_agent.user_id,
                    "name": updated_agent.name,
                    "description": updated_agent.description,
                    "system_prompt": updated_agent.system_prompt,
                    "language": updated_agent.language,
                    "voice": updated_agent.voice_id,
                    "multi_lingual_enabled": updated_agent.multi_lingual,
                    "first_message": updated_agent.first_message,
                    "first_message_mode": "assistant-speaks-first",
                    "end_call_message": updated_agent.end_call_message,
                    "end_call_function_enabled": False,
                    "recording_enabled": updated_agent.voice_recording_enabled,
                    "voicemail_message": None,
                    "summary_email": None,
                    "forwarding_number": None,
                    "actions": [],
                    "hipaa_enabled": False,
                    "timezone": updated_agent.timezone,
                    "providers": [],
                    "created_at": updated_agent.created_at,
                    "file_ids": [],
                    "detect_caller_number": False
                }
            }
        }
    async def get_agent_by_id(self, agent_id):
        result = await self.db.execute(
            select(Agent).where(Agent.id == agent_id)
        )
        return result.scalar_one_or_none()

    async def delete_agent(self, agent_id: UUID, user_id: UUID):
        agent = await self.repo.get_by_id(agent_id, user_id)
        if not agent:
            return None
        await self.repo.delete(agent)
        return True

    #  Prompt 

    async def get_prompt(self, agent_id: UUID, current_user):
        agent = await self._get_agent_or_none(agent_id, current_user.id)
        if not agent:
            return None

        return {
            "assistant_id": agent.id,
            **self._resolve_defaults(agent),
        }

    async def update_prompt(self, agent_id: UUID, current_user, data):
        agent = await self._get_agent_or_none(agent_id, current_user.id)
        if not agent:
            return {"success": False, "message": "Agent not found", "data": None}

        # Only overwrite fields that are explicitly provided and non-empty
        if data.first_message and data.first_message.strip():
            agent.first_message = data.first_message

        if data.system_prompt and data.system_prompt.strip():
            agent.system_prompt = data.system_prompt

        if data.end_call_message and data.end_call_message.strip():
            agent.end_call_message = data.end_call_message

        await self.db.commit()
        await self.db.refresh(agent)

        return {
            "status": True,
            "message": "Prompt updated successfully",
            "data": {
                "assistant_id": agent.id,
                **self._resolve_defaults(agent),
            },
        }
    # Ask Agent

    async def ask_agent(self, agent_id: UUID, user_id:UUID, query: str):
        agent = await self._get_agent_or_none(agent_id, user_id)
        if not agent:
            return {"success": False, "message": "Agent not found", "data": None}

        context = await self.retrieval.retrieve_context(query, user_id)
        system_prompt = agent.system_prompt or DEFAULT_AGENT_PROMPT["system_prompt"]

        answer = await self.llm.answer_with_prompt(
            query=query,
            context=context,
            system_prompt=system_prompt,
        )

        return {"status": True, "data": {"answer": answer, "agent_id": agent_id}}

    # Private Helpers 

    async def _get_agent_or_none(self, agent_id: UUID, user_id: int):
        """Fetch agent by id + user scope. Returns None if not found."""
        return await self.repo.get_by_id(agent_id, user_id)

    def _resolve_defaults(self, agent) -> dict:
        """Return prompt fields with DEFAULT_AGENT_PROMPT as fallback (never mutates agent)."""
        return {
            "first_message":    agent.first_message    or DEFAULT_AGENT_PROMPT["first_message"],
            "system_prompt":    agent.system_prompt    or DEFAULT_AGENT_PROMPT["system_prompt"],
            "end_call_message": agent.end_call_message or DEFAULT_AGENT_PROMPT["end_call_message"],
        }
