from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.future import select
from database import AsyncSessionLocal
from model import Token


class TokenAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        authorization: str = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            return JSONResponse(
                content={"detail": "Authorization header missing or invalid"},
                status_code=401,
            )

        token = authorization.split(" ")[1]

        try:
            async with AsyncSessionLocal() as db:
                query = select(Token).filter(Token.token == token)
                result = await db.execute(query)
                token_entry = result.scalars().first()

                if not token_entry:
                    raise ValueError("Invalid or expired token")

                request.state.token_entry = token_entry

            response = await call_next(request)
            return response

        except ValueError as exc:
            return JSONResponse(
                content={"detail": str(exc)},
                status_code=401,
            )

        except Exception as exc:
            return JSONResponse(
                content={"detail": f"Unexpected error: {str(exc)}"},
                status_code=500,
            )