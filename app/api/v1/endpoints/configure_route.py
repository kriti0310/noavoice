from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import StreamingResponse
from uuid import UUID
from sqlalchemy import select
from app.models.agent_model import Agent
from app.config.database import get_db
from app.schemas.configure_schema import ConfigureAgentRequest
from app.repository.configure_repository import ConfigureRepository
from app.services.elevenlabs_service import ElevenLabsService
import io


router = APIRouter(prefix="/configure", tags=["Configure"])

@router.get("/{agent_id}/voices")
async def get_voices(agent_id: UUID, db: AsyncSession = Depends(get_db)):

    result = await db.execute(
        select(Agent).where(Agent.id == agent_id, Agent.is_deleted == False)
    )
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    service = ElevenLabsService()

    voices = service.get_voices()

    return voices

@router.put("/{agent_id}")
async def configure_agent(
    agent_id:UUID,
    payload: ConfigureAgentRequest,
    db: AsyncSession = Depends(get_db)
):

    repo = ConfigureRepository(db)

    agent = await repo.get_agent(agent_id)

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    await repo.save_configuration(agent, payload.dict())

    return {"message": "Configuration saved successfully"}

@router.post("/{agent_id}/test")
async def test_voice(
    agent_id: UUID,
    text: str,
    db: AsyncSession = Depends(get_db)
):

    repo = ConfigureRepository(db)

    agent = await repo.get_agent(agent_id)

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    # 🔥 voice config comes directly from agent table
    if not agent.voice_id:
        raise HTTPException(
            status_code=400,
            detail="Voice not configured for this agent"
        )

    service = ElevenLabsService()

    audio = service.text_to_speech(agent.voice_id, text)
    if not audio:
        raise HTTPException(
            status_code=400,
            detail="Voice preview unavailable. ElevenLabs blocked or quota exceeded."
        )
    return StreamingResponse(io.BytesIO(audio), media_type="audio/mpeg")

@router.post("/{agent_id}/publish")
async def publish_agent(
    agent_id: UUID,
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(Agent).where(
            Agent.id == agent_id,
            Agent.is_deleted == False
        )
    )

    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    # Optional validation before publishing
    if not agent.voice_id:
        raise HTTPException(
            status_code=400,
            detail="Configure voice before publishing"
        )

    if not agent.language:
        raise HTTPException(
            status_code=400,
            detail="Select language before publishing"
        )

    agent.is_published = True

    await db.commit()

    return {"message": "Agent published successfully"}