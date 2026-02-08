"""
[Task]: T-B009
[From]: speckit.plan §1.3
[Purpose]: Common response schemas — error and success shapes
"""

from sqlmodel import SQLModel


class ErrorResponse(SQLModel):
    """Standard error response shape: { message, code }."""

    message: str
    code: str


class SuccessResponse(SQLModel):
    """Standard success response shape: { success: true }."""

    success: bool = True
