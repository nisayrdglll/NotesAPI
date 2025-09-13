from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import Note, NoteStatus, User, Role
from ..schemas import NoteCreate, NoteOut, Page, PageMeta
from ..deps import get_current_user
from sqlalchemy import func

router = APIRouter(prefix="/notes", tags=["notes"])

@router.post("", response_model=NoteOut, status_code=201, summary="Create note")
def create_note(
    body: NoteCreate,
    db: Session = Depends(get_db),
    me: User = Depends(get_current_user),
):
    note = Note(
        owner_id=me.id,
        raw_text=body.raw_text,
        status=NoteStatus.queued,
        attempts=0,
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note

@router.get("", response_model=Page[NoteOut], summary="List notes")
def list_notes(
    db: Session = Depends(get_db),
    me: User = Depends(get_current_user),
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    q = db.query(Note)
    if me.role != Role.ADMIN:
        q = q.filter(Note.owner_id == me.id)

    total = q.with_entities(func.count()).scalar()
    rows = q.order_by(Note.id.desc()).offset(offset).limit(limit).all()
    return Page[NoteOut](data=rows, meta=PageMeta(total=total, limit=limit, offset=offset))

@router.get("/{note_id}", response_model=NoteOut, summary="Get note by id")
def get_note(
    note_id: int,
    db: Session = Depends(get_db),
    me: User = Depends(get_current_user),
):
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(404, "Note not found")
    if me.role != Role.ADMIN and note.owner_id != me.id:
        raise HTTPException(403, "Forbidden")
    return note
