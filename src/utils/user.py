from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint


from src.data.db import SessionLocal
from src.resolvers.user_resolvers import get_user_by_token

class UserAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        session = SessionLocal()
        try:
            authorization = request.headers.get("Authorization")
            if not authorization:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Missing Authorization header"},
                )

            # Extract the token from the Authorization header
            token = authorization.split(" ")[1]
            user, profile = get_user_by_token(token=token, session=session)
            request.state.user = user
            request.state.profile = profile
            request.state.session = session
            
            response = await call_next(request)
            return response
        except HTTPException as e:
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail},
            )
        except Exception as e:
            print("error==========", e)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": str(e)},
            )
        finally:
            session.close()