from sqlalchemy.ext.asyncio import AsyncSession
from app.models.knowledge_model import KnowledgeBase
from uuid import UUID
from sqlalchemy import select, delete
from app.models.file import File

class KnowledgeRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def bulk_insert(self, user_id: UUID, file_id: UUID, chunks: list):

        records = []

        for item in chunks:
            records.append(
                KnowledgeBase(
                    user_id=user_id,
                    file_id=file_id,
                    content=item["content"],
                    embedding=item["embedding"]
                )
            )

        self.db.add_all(records)
        await self.db.commit()

        return records
    

    # DELETE FILE RECORD
    async def delete_by_file_id(self, file_id: UUID):
        await self.db.execute(
            delete(KnowledgeBase).where(KnowledgeBase.file_id == file_id)
        )
        await self.db.commit()
