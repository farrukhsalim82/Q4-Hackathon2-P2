"""
[Task]: T-B008
[From]: speckit.plan §1.3
[Purpose]: Todo request/response schemas — camelCase output for frontend contract
"""

from datetime import datetime

from sqlmodel import Field, SQLModel


class TodoCreate(SQLModel):
    """Request schema for creating a new todo."""

    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)


class TodoUpdate(SQLModel):
    """Request schema for updating an existing todo (all fields optional)."""

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    completed: bool | None = None


class TodoResponse(SQLModel):
    """Response schema for a single todo — camelCase fields for frontend."""

    id: str
    title: str
    description: str | None
    completed: bool
    createdAt: datetime
    updatedAt: datetime

    @classmethod
    def from_model(cls, todo: "Todo") -> "TodoResponse":  # noqa: F821
        """Convert a Todo ORM model to a response schema."""
        return cls(
            id=todo.id,
            title=todo.title,
            description=todo.description,
            completed=todo.completed,
            createdAt=todo.created_at,
            updatedAt=todo.updated_at,
        )


class TodoListResponse(SQLModel):
    """Response schema for a list of todos."""

    todos: list[TodoResponse]


class TodoSingleResponse(SQLModel):
    """Response schema wrapping a single todo."""

    todo: TodoResponse
