from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.agent_repository import AgentRepository
from app.schemas.agent_schema import AgentCreate, AgentUpdate, AgentResponse
from app.services.retrieval_service import RetrievalService
from app.services.llm_service import LLMService
from app.config.default_prompt import DEFAULT_AGENT_PROMPT
from uuid import UUID
from app.services.default_template import load_default_template

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

        return {
            "status": True,
            "message": "",
            "data": {
                "assistants": agents
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
                "assistant": agent
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
                "assistant": updated_agent
            }
        }

    async def delete_agent(self, agent_id: UUID, user_id: UUID):
        agent = await self.repo.get_by_id(agent_id, user_id)
        if not agent:
            return None
        await self.repo.delete(agent)
        return True
    
    # def _build_agent_response(self, agent, template) -> dict:
    #     t = template
    #     return {
    #         # ── From Agent ──
    #         "id":          agent.id,
    #         "name":        agent.name,
    #         "description": agent.description,
    #         "created_at":  agent.created_at,

    #         # ── From Template ──
    #         "system_prompt":               t.system_prompt              if t else None,
    #         "first_message":               t.first_message              if t else None,
    #         "end_call_message":            t.end_call_message           if t else None,
    #         "language":                    t.language                   if t else "EN",
    #         "voice_id":                    t.voice_id                   if t else None,
    #         "voice_provider":              t.voice_provider             if t else "elevenlabs",
    #         "multi_lingual":               t.multi_lingual              if t else False,
    #         "voice_recording_enabled":     t.voice_recording_enabled    if t else False,
    #         "is_published":                False,
    #     }

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

    async def delete_prompt(self, agent_id: UUID, current_user):
        agent = await self._get_agent_or_none(agent_id, current_user.id)
        if not agent:
            return {"success": False, "message": "Agent not found", "data": None}

        agent.first_message = None
        agent.system_prompt = None
        agent.end_call_message = None

        await self.db.commit()
        await self.db.refresh(agent)

        return {"status": True, "message": "Prompt reset to default", "data": None}

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

    # def _build_full_response(self, agent):

    #     return {
    #         "id": agent.id,
    #         "company_id": None,  # if not implemented
    #         "name": agent.name,
    #         "description": agent.description,

    #         "system_prompt": agent.system_prompt,
    #         "language": agent.language,
    #         "voice": agent.voice_id,
    #         "multi_lingual": agent.multi_lingual,

    #         "first_message": agent.first_message,
    #         "first_message_mode": "assistant-speaks-first",

    #         "end_call_message": agent.end_call_message,
    #         "end_call_function_enabled": False,

    #         "recording_enabled": agent.voice_recording_enabled,
    #         "voicemail_message": None,

    #         "summary_email": None,
    #         "forwarding_number": None,
    #         "actions": [],
    #         "hipaa_enabled": False,
    #         "timezone": "UTC",
    #         "providers": [],
    #         "created_at": agent.created_at,
    #         "file_ids": [],
    #         "detect_caller_number": False,
    #     }