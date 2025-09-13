# app/schemas.py
from __future__ import annotations
from typing import Generic, TypeVar, List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr

from .models import Role, NoteStatus

# ---------- Auth ----------
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: Optional[Role] = None

class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: Role
    created_at: datetime

    class Config:
        from_attributes = True

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

# ---------- Notes ----------
class NoteCreate(BaseModel):
    raw_text: str

class NoteOut(BaseModel):
    id: int
    owner_id: int
    raw_text: str
    summary: Optional[str]
    status: NoteStatus
    attempts: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

# ---------- Pagination ----------
T = TypeVar("T")

class PageMeta(BaseModel):
    total: int
    limit: int
    offset: int

class Page(BaseModel, Generic[T]):
    data: List[T]
    meta: PageMeta

# ---------- Standard Error schema ----------
class ErrorResponse(BaseModel):
    detail: str
    code: Optional[str] = None
