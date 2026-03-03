
from fastapi import APIRouter
from pydantic import BaseModel
from app.tools.tool import execute_tool

router = APIRouter()

class ToolRequest(BaseModel):
    tool_name: str
    tool_args: dict
    session_id: str | None = None

@router.post("/tools/execute")
async def run_tool(request: ToolRequest):
    result = await execute_tool(
        request.tool_name,
        request.tool_args,
        request.session_id
    )
    return {"result": result}