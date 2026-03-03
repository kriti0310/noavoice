import os
import uuid
import requests
from fastapi import HTTPException
from fastapi.responses import FileResponse
from app.services.embedding_service import EmbeddingService
from app.repository.knowledge_repository import KnowledgeRepository
from app.repository.file_repository import FileRepository
from app.models.file import File
from sqlalchemy import select

class KnowledgeService:

    def __init__(self, db):
        self.db = db
        self.embedding_service = EmbeddingService()
        self.repo = KnowledgeRepository(db)
        self.file_repo = FileRepository(db)

    async def upload_knowledge(self, current_user, file=None, url=None):
        try:
            if not file and not url:
                raise ValueError("Either file or url must be provided")

            os.makedirs("uploads", exist_ok=True)

            file_id = uuid.uuid4()

            # -------- HANDLE FILE --------
            if file:
                file_path = f"uploads/{file_id}_{file.filename}"

                content = await file.read()
                file_size = len(content)
                mimetype = file.content_type

                with open(file_path, "wb") as buffer:
                    buffer.write(content)

                original_name = file.filename

            # -------- HANDLE URL --------
            else:
                response = requests.get(url)
                response.raise_for_status()

                content = response.content
                file_size = len(content)
                mimetype = response.headers.get("Content-Type", "text/plain")

                file_path = f"uploads/{file_id}.txt"

                with open(file_path, "wb") as f:
                    f.write(response.content)

                original_name = url.split("/")[-1] or "url_content.txt"

            # -------- CREATE FILE RECORD --------
            file_record = File(
                id=file_id,
                user_id=current_user.id,
                original_name=original_name,
                storage_path=file_path,
                file_size=file_size,        
                mimetype=mimetype,         
                url=url if url else None,
                status="processing"
            )

            file_record = await self.file_repo.create(file_record)

            # -------- EMBEDDING PIPELINE --------
            chunks = await self.embedding_service.process_file(file_path)

            await self.repo.bulk_insert(
                user_id=current_user.id,
                file_id=file_record.id,
                chunks=chunks
            )

            # -------- UPDATE STATUS --------
            await self.file_repo.update_status(file_record, "ready")

        #     # -------- CLEANUP --------
        #     os.remove(file_path)

            return {
                "status": True,
                "message": "Knowledge processed & stored",
                "data": {
                    "file_id": str(file_record.id),
                    "chunks_created": len(chunks)
                }
            }
        except Exception as e:

            # update status if failure
            if 'file_record' in locals():
                await self.file_repo.update_status(file_record, "failed")

            raise e

        # finally:
        #     # -------- AUTO DELETE LOCAL FILE --------
        #     if file_path and os.path.exists(file_path):
        #         os.remove(file_path)
        #         print("Local file deleted:", file_path)

    async def list_knowledge(
        self,
        current_user,
        search: str | None = None,
        sort_by: str = "created_at",
        order: str = "desc",
        limit: int = 10,
        offset: int = 0
    ):

        files = await self.file_repo.list_files(
            user_id=current_user.id,
            search=search,
            sort_by=sort_by,
            order=order,
            limit=limit,
            offset=offset
            )
        if not files:
            return {
                "status": True,
                "message": "No documents found",
                "data": []
            }

        return {
            "status": True,
            "message": "Knowledge fetched",
            "data": [
                {
                    "file_id": str(file.id),
                    "name": file.original_name,
                    "file_size": file.file_size,
                    "mimetype": file.mimetype,
                    "status": file.status,
                    "created_at": file.created_at,
                    "updated_at": file.updated_at
                }
                for file in files
            ]
        }
    async def delete_knowledge(self, file_id, current_user):

        file = await self.file_repo.get_by_id(file_id=file_id,user_id=current_user.id)

        if not file:
            raise ValueError("File not found")
        
        # delete embeddings first
        await self.repo.delete_by_file_id(file_id)

        # delete file record
        await self.file_repo.delete(file)

        return {
            "status": True,
            "message": "Knowledge deleted successfully"
        }
    
    async def get_stats(self, current_user):

        stats = await self.file_repo.get_stats(current_user.id)

        total, processed, pending, storage = stats

        return {
            "status": True,
            "message": "Knowledge stats fetched",
            "data": {
                "total_documents": total,
                "processed": processed,
                "pending": pending,
                "storage_used_bytes": storage,
                "storage_used_mb": round(storage / (1024 * 1024), 2)
            }
        }

    async def view_knowledge(self, file_id, current_user):

        file = await self.file_repo.get_by_id(
            file_id=file_id,
            user_id=current_user.id
        )

        if not file:
            raise HTTPException(status_code=404, detail="File not found")

        if not os.path.exists(file.storage_path):
            raise HTTPException(status_code=404, detail="Physical file missing")

        return FileResponse(
            path=file.storage_path,
            media_type=file.mimetype,
            headers={
                "Content-Disposition": f'inline; filename="{file.original_name}"'
    }
        )