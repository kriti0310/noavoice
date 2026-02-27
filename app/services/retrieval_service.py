from sqlalchemy import select
from openai import AsyncOpenAI
from app.models.knowledge_model import KnowledgeBase
from app.config.settings import settings
from uuid import UUID


client = AsyncOpenAI(
    api_key=settings.OPENAI_API_KEY,
    base_url="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "NoaVoice"
    }
)


class RetrievalService:

    def __init__(self, db):
        self.db = db

    async def generate_query_embedding(self, query: str):

        response = await client.embeddings.create(
            model="openai/text-embedding-3-small",
            input=query
        )

        return response.data[0].embedding

    async def retrieve_context(self, query: str, user_id: UUID, limit=5):

        query_embedding = await self.generate_query_embedding(query)

        stmt = (
            select(KnowledgeBase)
            .where(KnowledgeBase.user_id == user_id)
            .order_by(
                KnowledgeBase.embedding.cosine_distance(query_embedding)
            )
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        matches = result.scalars().all()

        return [m.content for m in matches]