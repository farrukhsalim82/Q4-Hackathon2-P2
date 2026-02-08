"""
[Task]: T-B012
[From]: speckit.plan §5.3
[Purpose]: Auth session-check router — convenience endpoint for verifying session cookies.
           Better Auth itself runs on the frontend; this just reads the shared DB.
"""

from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.get("/session")
async def check_session(
    current_user: dict = Depends(get_current_user),
) -> dict:
    """Return the authenticated user from the session cookie.

    Used for testing auth flow. Actual Better Auth routes (sign-up, sign-in,
    sign-out) are handled by the frontend's Next.js server.
    """
    return {"user": current_user}
