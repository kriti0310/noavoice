from fastapi import Depends, APIRouter, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.config.database import get_db
from app.services.agent_service import AgentService
from app.schemas.prompt_schema import AgentPromptUpdate, AgentPromptResponse
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/agents", tags=["Prompts"])


@router.get("/{agent_id}/prompt", response_model=AgentPromptResponse)
async def get_prompt(
    agent_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await AgentService(db).get_prompt(agent_id, current_user)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    return result


@router.put("/{agent_id}/prompt", response_model=AgentPromptResponse)
async def update_prompt(
    agent_id: UUID,
    payload: AgentPromptUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await AgentService(db).update_prompt(
        agent_id=agent_id,
        current_user=current_user,
        data=payload,
    )

    if not result.get("status"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result.get("message"))

    return result["data"]


@router.delete("/{agent_id}/prompt", status_code=status.HTTP_200_OK)
async def delete_prompt(
    agent_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await AgentService(db).delete_prompt(agent_id, current_user)

    if not result.get("status"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result.get("message"))

    return result