"""
[Task]: T-B013
[From]: speckit.plan §3.1, §5.1, §5.2
[Purpose]: FastAPI app assembly — CORS, lifespan, exception handlers, router mounts
"""

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine
from app.routers import auth, todos
from app.utils.exceptions import register_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage app lifecycle: dispose connection pool on shutdown."""
    yield
    await engine.dispose()


app = FastAPI(title="Todo API", lifespan=lifespan)

# --- CORS (outermost middleware) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Exception handlers ---
register_exception_handlers(app)

# --- Router mounts ---
app.include_router(auth.router)
app.include_router(todos.router)


# --- Health check ---
@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint — returns 200 if the server is running."""
    return {"status": "ok"}
