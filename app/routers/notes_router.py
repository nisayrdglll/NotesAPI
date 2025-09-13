from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from .auth_router import router
from ..db import get_db
from ..models import Note, NoteStatus, User, Role
from ..schemas import NoteCreate, NoteOut, Page, PageMeta
from ..deps import get_current_user

@router.get("", response_model=Page[NoteOut], summary="List notes with pagination & filters")
def list_notes(
    db: Session = Depends(get_db),
    me: User = Depends(get_current_user),

    # Sayfalama
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0),

    # Filtreler
    status: Optional[NoteStatus] = Query(default=None, description="queued|processing|done|failed"),
    q: Optional[str] = Query(default=None, description="raw_text içinde arama"),
    created_from: Optional[datetime] = Query(default=None),
    created_to: Optional[datetime] = Query(default=None),

    # Sıralama
    order_by: str = Query("id", regex="^(id|created_at|updated_at)$"),
    order_dir: str = Query("desc", regex="^(asc|desc)$"),
):
    qset = db.query(Note)
    if me.role != Role.ADMIN:
        qset = qset.filter(Note.owner_id == me.id)
    # Filtreler
    if status:
        qset = qset.filter(Note.status == status)
    if q:
        qset = qset.filter(Note.raw_text.ilike(f"%{q}%"))
    if created_from:
        qset = qset.filter(Note.created_at >= created_from)
    if created_to:
        qset = qset.filter(Note.created_at <= created_to)

    # Toplam
    total = qset.with_entities(func.count()).scalar()

    # Sıralama
    col = {"id": Note.id, "created_at": Note.created_at, "updated_at": Note.updated_at}[order_by]
    if order_dir == "desc":
        col = col.desc()
    qset = qset.order_by(col)

    rows = qset.offset(offset).limit(limit).all()

    return Page[NoteOut](data=rows, meta=PageMeta(total=total, limit=limit, offset=offset))
