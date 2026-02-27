from app.services.retrieval_service import RetrievalService
from app.services.llm_service import LLMService


class AgentQueryService:

    def __init__(self, db):
        self.retrieval = RetrievalService(db)
        self.llm = LLMService()

    async def ask(self, query, user):

        context = await self.retrieval.retrieve_context(query, user.id)
        answer = await self.llm.answer(query, context)

        return {
            "status": True,
            "data": {
                "answer": answer
            }
        }
