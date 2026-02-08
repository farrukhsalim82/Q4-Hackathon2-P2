"""
[Task]: T-B015, T-B016, T-B017, T-B018, T-B020
[From]: speckit.plan §2.1, §2.2
[Purpose]: Todo CRUD + toggle endpoints — all queries scoped to authenticated user
"""

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.database import get_session
from app.dependencies.auth import get_current_user
from app.models.todo import Todo
from app.schemas.common import SuccessResponse
from app.schemas.todo import (
    TodoCreate,
    TodoListResponse,
    TodoResponse,
    TodoSingleResponse,
    TodoUpdate,
)

router = APIRouter(prefix="/api/todos", tags=["todos"])


def _validate_uuid(todo_id: str) -> None:
    """Validate that todo_id is a valid UUID format. Raises 404 if not."""
    try:
        UUID(todo_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Todo not found")


# ---------------------------------------------------------------------------
# T-B015: GET /api/todos — List all todos for the authenticated user
# ---------------------------------------------------------------------------


@router.get("/", response_model=TodoListResponse)
async def list_todos(
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
) -> TodoListResponse:
    """Return all todos for the authenticated user, ordered by created_at DESC."""
    statement = (
        select(Todo)
        .where(Todo.user_id == current_user["id"])
        .order_by(Todo.created_at.desc())
    )
    result = await session.execute(statement)
    todos = result.scalars().all()
    return TodoListResponse(
        todos=[TodoResponse.from_model(t) for t in todos]
    )


# ---------------------------------------------------------------------------
# T-B016: POST /api/todos — Create a new todo
# ---------------------------------------------------------------------------


@router.post("/", response_model=TodoSingleResponse, status_code=201)
async def create_todo(
    data: TodoCreate,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
) -> TodoSingleResponse:
    """Create a new todo for the authenticated user with completed=false."""
    todo = Todo(
        user_id=current_user["id"],
        title=data.title,
        description=data.description,
    )
    session.add(todo)
    await session.flush()
    await session.refresh(todo)
    return TodoSingleResponse(todo=TodoResponse.from_model(todo))


# ---------------------------------------------------------------------------
# T-B017: PUT /api/todos/{id} — Update a todo (partial)
# ---------------------------------------------------------------------------


@router.put("/{todo_id}", response_model=TodoSingleResponse)
async def update_todo(
    todo_id: str,
    data: TodoUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
) -> TodoSingleResponse:
    """Update a todo owned by the authenticated user. Only non-None fields are applied."""
    _validate_uuid(todo_id)

    statement = select(Todo).where(
        Todo.id == todo_id,
        Todo.user_id == current_user["id"],
    )
    result = await session.execute(statement)
    todo = result.scalar_one_or_none()

    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    if data.title is not None:
        todo.title = data.title
    if data.description is not None:
        todo.description = data.description
    if data.completed is not None:
        todo.completed = data.completed

    todo.updated_at = datetime.now(timezone.utc)

    session.add(todo)
    await session.flush()
    await session.refresh(todo)
    return TodoSingleResponse(todo=TodoResponse.from_model(todo))


# ---------------------------------------------------------------------------
# T-B018: DELETE /api/todos/{id} — Delete a todo
# ---------------------------------------------------------------------------


@router.delete("/{todo_id}", response_model=SuccessResponse)
async def delete_todo(
    todo_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
) -> SuccessResponse:
    """Permanently delete a todo owned by the authenticated user."""
    _validate_uuid(todo_id)

    statement = select(Todo).where(
        Todo.id == todo_id,
        Todo.user_id == current_user["id"],
    )
    result = await session.execute(statement)
    todo = result.scalar_one_or_none()

    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    await session.delete(todo)
    await session.flush()
    return SuccessResponse()


# ---------------------------------------------------------------------------
# T-B020: PATCH /api/todos/{id}/toggle — Toggle completion status
# ---------------------------------------------------------------------------


@router.patch("/{todo_id}/toggle", response_model=TodoSingleResponse)
async def toggle_todo(
    todo_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
) -> TodoSingleResponse:
    """Flip the completed boolean for a todo owned by the authenticated user."""
    _validate_uuid(todo_id)

    statement = select(Todo).where(
        Todo.id == todo_id,
        Todo.user_id == current_user["id"],
    )
    result = await session.execute(statement)
    todo = result.scalar_one_or_none()

    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    todo.completed = not todo.completed
    todo.updated_at = datetime.now(timezone.utc)

    session.add(todo)
    await session.flush()
    await session.refresh(todo)
    return TodoSingleResponse(todo=TodoResponse.from_model(todo))
