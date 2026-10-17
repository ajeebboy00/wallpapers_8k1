from typing import Any, Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

DataT = TypeVar("DataT")

class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[Any] = None

class StandardResponse(BaseModel, Generic[DataT]):
    success: bool = True
    data: Optional[DataT] = None
    message: Optional[str] = "Operation completed successfully"
    error: Optional[ErrorDetail] = None

class PaginationMeta(BaseModel):
    page: int
    limit: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool

class PaginatedResponse(BaseModel, Generic[DataT]):
    success: bool = True
    data: List[DataT]
    meta: PaginationMeta
    message: Optional[str] = "Records retrieved successfully"
