from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from conf import ADMIN_TOKEN, ENV
from src.data.db import SessionLocal
from src.resolvers.user_resolvers import get_user_by_token


class UserAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        session = SessionLocal()
        params = request.query_params

        if params and params.get("dev"):
            request.state.user = None
            request.state.profile = None
            request.state.session = session
            response = await call_next(request)
            return response

        try:
            authorization = request.headers.get("Authorization")
            if not authorization:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Missing Authorization header"},
                )
            # Extract the token from the Authorization header
            token = authorization.split(" ")[1]

            if ENV == "dev" and token == ADMIN_TOKEN:
                request.state.user = None
                request.state.profile = None
                request.state.session = session
                response = await call_next(request)
                return response

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
