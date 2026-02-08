"""
[Task]: T-B007
[From]: speckit.plan §1.2, speckit.specify §Key Entities
[Purpose]: Todo SQLModel table model with all fields and constraints
"""

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Column, DateTime, String, func
from sqlmodel import Field, SQLModel


class Todo(SQLModel, table=True):
    __tablename__ = "todo"

    id: str = Field(
        default_factory=lambda: str(uuid4()),
        primary_key=True,
    )
    user_id: str = Field(
        sa_column=Column(String, nullable=False, index=True),
    )
    title: str = Field(
        sa_column=Column(String(200), nullable=False),
    )
    description: str | None = Field(
        default=None,
        sa_column=Column(String(2000), nullable=True),
    )
    completed: bool = Field(default=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        ),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
        ),
    )
