from fastapi import APIRouter
from app.api.v1.endpoints.users import router as user_router
from app.api.v1.endpoints.auth_route import router as auth_router
from app.api.v1.endpoints.agent_route import router as agent_router
from app.api.v1.endpoints.knowledge_route import router as knowledge_router
from app.api.v1.endpoints.agent_chat import router as chat_router
from app.api.v1.endpoints.prompt_route import router as prompt_router
from app.api.v1.endpoints.configure_route import router as configure_router
from app.api.v1.endpoints.tool_route import router as tool_router

router = APIRouter()

router.include_router(user_router)
router.include_router(auth_router)
router.include_router(agent_router)
router.include_router(knowledge_router)
router.include_router(chat_router)
router.include_router(prompt_router)
router.include_router(configure_router)
router.include_router(tool_router)