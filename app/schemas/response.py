from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar("T")

class APIResponse(BaseModel, Generic[T]):
    status: bool
    message: str
    data: Optional[T] = None

    model_config = {
        "arbitrary_types_allowed": True
    }