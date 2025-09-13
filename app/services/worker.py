import time
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..db import SessionLocal
from ..models import Note, NoteStatus
from .summarize import simple_summarize

MAX_RETRIES = 3

def _process_one(db: Session) -> bool:
    now = datetime.now(timezone.utc)
    note = db.execute(
        select(Note)
        .where(
            ((Note.status == NoteStatus.QUEUED) |
             ((Note.status == NoteStatus.PROCESSING) & (Note.next_attempt_at <= now)))
        )
        .order_by(Note.id.asc())
        .with_for_update(skip_locked=True)
    ).scalars().first()

    if not note:
        return False

    note.status = NoteStatus.PROCESSING
    db.commit(); db.refresh(note)

    try:
        summary = simple_summarize(note.raw_text)
        note.summary = summary
        note.status = NoteStatus.DONE
        note.attempts += 1
        note.next_attempt_at = now
        db.commit()
    except Exception:
        note.attempts += 1
        if note.attempts >= MAX_RETRIES:
            note.status = NoteStatus.FAILED
        else:
            backoff = 2 ** note.attempts
            note.next_attempt_at = now + timedelta(seconds=backoff)
        db.commit()
    return True

def worker_loop():
    while True:
        with SessionLocal() as db:
            worked = _process_one(db)
        time.sleep(0.5 if worked else 2.0)
