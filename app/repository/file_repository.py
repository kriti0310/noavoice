from app.models.file import File
from sqlalchemy import select,func,asc, desc
from uuid import UUID
from typing import Optional
class FileRepository:

    def __init__(self, db):
        self.db = db

    async def create(self, file: File):
        self.db.add(file)
        await self.db.commit()
        await self.db.refresh(file)
        return file

    async def update_status(self, file: File, status: str):
        file.status = status
        await self.db.commit()

     
    async def get_by_id(self, file_id: UUID):
        result = await self.db.execute(
            select(File).where(File.id == file_id)
        )
        return result.scalar_one_or_none()

    # ✅ ADD THIS (if not already)
    async def delete(self, file: File):
        await self.db.delete(file)
        await self.db.commit()

    async def get_stats(self, user_id: UUID):
        result = await self.db.execute(
            select(
                func.count(File.id).label("total"),
                func.count().filter(File.status == "ready").label("processed"),
                func.count().filter(File.status == "processing").label("pending"),
                func.coalesce(func.sum(File.file_size), 0).label("storage")
            ).where(File.user_id == user_id)
        )

        return result.one()
    
    async def list_files(
        self,
        user_id: UUID,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        order: str = "desc",
        limit: int = 10,
        offset: int = 0
    ):
        query = select(File).where(File.user_id == user_id)

        # 🔎 SEARCH
        if search:
            search = search.strip()
            normalized = search.replace(" ", "_")
            query = query.where(
                func.lower(File.original_name).contains(normalized.lower())
            )

        # 🔀 SORTING (Safe Columns Only)
        allowed_sort_fields = {
            "name": File.original_name,
            "created_at": File.created_at,
            "file_size": File.file_size,
            "status": File.status
        }

        sort_column = allowed_sort_fields.get(sort_by, File.created_at)

        if order == "asc":
            query = query.order_by(asc(sort_column))
        else:
            query = query.order_by(desc(sort_column))

        # 📄 PAGINATION
        query = query.limit(limit).offset(offset)

        result = await self.db.execute(query)
        return result.scalars().all()