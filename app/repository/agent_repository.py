from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from app.models.agent_model import Agent
from app.schemas.agent_schema import AgentCreate, AgentUpdate


class AgentRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # CREATE AGENT
    async def create(self, user_id:UUID, data: AgentCreate) -> Agent:
        agent = Agent(
            user_id=user_id,
            name=data.name,
            description=data.description,
        )
        self.db.add(agent)
        await self.db.commit()
        await self.db.refresh(agent)
        return agent

    # GET ALL (user scoped)
    async def get_all(self, user_id: UUID, skip: int = 0, limit: int = 20) -> List[Agent]:
        result = await self.db.execute(
            select(Agent)
            .where(
                Agent.user_id == user_id,
                Agent.is_deleted == False,
                Agent.is_template == False
            )
            .offset(skip)
            .limit(limit)
            .order_by(Agent.created_at.desc())
        )
        return result.scalars().all()

    # GET BY ID
    async def get_by_id(self, agent_id:UUID, user_id: UUID) -> Optional[Agent]:
        result = await self.db.execute(
            select(Agent).where(
                Agent.id == agent_id,
                Agent.user_id == user_id,
                Agent.is_deleted == False,
                Agent.is_template == False
            )
        )
        return result.scalars().first()

    # update agent
    async def update(self, agent: Agent, data: AgentUpdate) -> Agent:
        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(agent, field, value)

        await self.db.commit()
        await self.db.refresh(agent)

        return agent

    # SOFT DELETE
    async def delete(self, agent: Agent):
        agent.is_deleted = True
        await self.db.commit()


    #Update agent prompt
    async def update_prompt(self, agent_id:UUID, prompt_data: dict):

        result = await self.db.execute(
            select(Agent).where(Agent.id == agent_id)
        )
        agent = result.scalar_one_or_none()

        if not agent:
            return None

        agent.first_message = prompt_data.get("first_message")
        agent.system_prompt = prompt_data.get("system_prompt")
        agent.end_call_message = prompt_data.get("end_call_message")

        await self.db.commit()
        await self.db.refresh(agent)

        return agent

    