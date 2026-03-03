from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.services.knowledge_service import KnowledgeService
from app.config.database import get_db
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/knowledge", tags=["Knowledge"])


@router.post("/upload")
async def upload_knowledge(
    file: UploadFile = File(None),
    url: str = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):

    if not file and not url:
        raise HTTPException(400, "Either file or url required")

    if file and url:
        raise HTTPException(400, "Upload file OR provide url, not both")

    return await KnowledgeService(db).upload_knowledge(
        current_user=current_user,
        file=file,
        url=url
)


@router.delete("/{file_id}")
async def delete_knowledge(
    file_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return await KnowledgeService(db).delete_knowledge(file_id, current_user)

@router.get("")
async def list_knowledge(
    search: str | None = None,
    sort_by: str = "created_at",
    order: str = "desc",
    limit: int = 10,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return await KnowledgeService(db).list_knowledge(
        current_user=current_user,
        search=search,
        sort_by=sort_by,
        order=order,
        limit=limit,
        offset=offset
    )

@router.get("/stats")
async def get_knowledge_stats(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return await KnowledgeService(db).get_stats(current_user)

async def get_by_id(self, file_id, current_user):
    query = select(Knowledge).where(
        Knowledge.id == file_id,
        Knowledge.company_id == current_user.company_id   # important for security
    )

    result = await self.db.execute(query)
    knowledge = result.scalar_one_or_none()

    if not knowledge:
        raise HTTPException(status_code=404, detail="File not found")

    return knowledge
    
@router.get("/{file_id}/view")
async def view_knowledge(
    file_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return await KnowledgeService(db).view_knowledge(file_id, current_user)