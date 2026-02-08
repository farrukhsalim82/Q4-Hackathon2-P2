"""
[Task]: T-B011
[From]: speckit.plan §0.4
[Purpose]: Session cookie validation — read Better Auth session from shared DB, resolve user
"""

from datetime import datetime, timezone

from fastapi import Depends, HTTPException, Request
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session

COOKIE_NAME = "better-auth.session_token"


async def get_current_user(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Validate the Better Auth session cookie and return the authenticated user.

    Reads the session token from the cookie, queries the shared session/user
    tables in Neon, and returns a dict with {id, email, name}.
    Raises HTTP 401 if the cookie is missing, session is invalid/expired,
    or user is not found.
    """
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Query the Better Auth session table (camelCase columns → raw SQL)
    result = await session.execute(
        text(
            'SELECT s."userId", s."expiresAt" '
            'FROM "session" s WHERE s.token = :token'
        ),
        {"token": token},
    )
    session_row = result.first()

    if not session_row:
        raise HTTPException(status_code=401, detail="Invalid session")

    user_id, expires_at = session_row

    # Check session expiration
    if expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Session expired")

    # Query the Better Auth user table
    user_result = await session.execute(
        text('SELECT id, email, name FROM "user" WHERE id = :id'),
        {"id": user_id},
    )
    user_row = user_result.first()

    if not user_row:
        raise HTTPException(status_code=401, detail="User not found")

    return {"id": user_row[0], "email": user_row[1], "name": user_row[2]}
