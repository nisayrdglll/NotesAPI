from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from .routers import auth_router, notes_router
from .services.worker import worker_loop
from .error_handlers import (
    http_exception_handler,
    validation_exception_handler,
    unhandled_exception_handler,
)
import threading

app = FastAPI(
    title="Notes API",
    version="1.1.0",
    description="JWT auth, role-based tenancy, async summarize job, pagination & filters",
)

# Routerlar
app.include_router(auth_router.router)
app.include_router(notes_router.router)

# Global error handlers
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

@app.exception_handler(Exception)
async def _unhandled(request: Request, exc: Exception):
    return await unhandled_exception_handler(request, exc)

# Worker thread
@app.on_event("startup")
def start_worker():
    t = threading.Thread(target=worker_loop, daemon=True)
    t.start()

@app.get("/health")
def health():
    return {"status": "ok"}
