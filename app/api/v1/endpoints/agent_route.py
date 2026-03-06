from fastapi import APIRouter, Depends, HTTPException,Header
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.config.database import get_db
from app.services.agent_service import AgentService
from app.schemas.agent_schema import AgentCreate, AgentUpdate, AgentResponse ,SingleAgentData, AgentListData
from app.utils.dependencies import get_current_user
from app.schemas.response import APIResponse
import os
router = APIRouter(prefix="/agents", tags=["Agents"])


@router.post("/create",response_model=APIResponse[SingleAgentData])
async def create_agent(payload: AgentCreate,db:
    AsyncSession = Depends(get_db),user=Depends(get_current_user)):
    service = AgentService(db)
    return await service.create_agent(user.id, payload)


@router.get("/get_all",response_model=APIResponse[AgentListData])
async def list_agents(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    service = AgentService(db)
    return await service.list_agents(user.id)


@router.get("/get/{agent_id}", response_model=APIResponse[SingleAgentData])
async def get_agent(
    agent_id: UUID,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    service = AgentService(db)

    result = await service.get_agent(agent_id, user.id)

    if not result:
        raise HTTPException(status_code=404, detail="Agent not found")

    return result    

@router.put("/update/{agent_id}",response_model=APIResponse[SingleAgentData])
async def update_agent(
    agent_id:UUID,
    payload: AgentUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    service = AgentService(db)
    agent = await service.update_agent(agent_id, user.id, payload)
    if not agent:
        raise HTTPException(404, "Agent not found")
    return agent


@router.delete("/delete/{agent_id}")
async def delete_agent(
    agent_id:UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    service = AgentService(db)
    success = await service.delete_agent(agent_id, user.id)
    if not success:
        raise HTTPException(404, "Agent not found")
    return {"message": "Agent deleted"}

# In your agents router
@router.get("/{agent_id}/internal", response_model=APIResponse[SingleAgentData])
async def get_agent_internal(
        agent_id: UUID,
        x_internal_key: str = Header(None),
        db: AsyncSession = Depends(get_db),
    ):

        if x_internal_key != os.getenv("SECRET_KEY"):
            raise HTTPException(status_code=401, detail="Unauthorized")

        service = AgentService(db)

        result = await service.get_agent_by_id(agent_id)

        if not result:
            raise HTTPException(status_code=404, detail="Agent not found")

        return APIResponse(
            status=True,
            message="Agent fetched",
            data={
            "assistant": result
    }
        )