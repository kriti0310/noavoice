from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.agent_query_service import AgentQueryService
from app.config.database import get_db
from app.utils.dependencies import get_current_user


router = APIRouter(prefix="/agent", tags=["Agent Chat"])


@router.post("/chat")
async def chat_agent(
    query: str,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):

    return await AgentQueryService(db).ask(query, user)
