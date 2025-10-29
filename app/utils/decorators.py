from fastapi import HTTPException, status, Request
from app.core.logger import logger
from functools import wraps 
import inspect

def login_required(func):
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        if not hasattr(request.state, "user"):
            raise HTTPException(status_code=401, detail="Authentication required here")
        result = func(request, *args, **kwargs)
        if inspect.isawaitable(result):
            result = await result
        return result
    return wrapper


PUBLIC_ROUTES = [
    "/auth/login",
    "/auth/register",
    "/openapi.json",
    "/docs",
    "/redoc"
]

def admin_required(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Find the Request object
        request: Request = kwargs.get("request") or next(
            (a for a in args if isinstance(a, Request)), None
        )
        if request is None:
            raise HTTPException(status_code=500, detail="Request object not found")

        # Skip admin check for public routes
        if request.url.path in PUBLIC_ROUTES:
            result = func(*args, **kwargs)
            return await result if inspect.isawaitable(result) else result

        # Check user
        user = getattr(request.state, "user", None)
        if not user:
            logger.warning(f"Unauthorized admin access attempt {request.state}")
            raise HTTPException(status_code=401, detail="Not authenticated")

        if user.role != "admin":
            logger.warning(f"User '{user.username}' tried to access admin area")
            raise HTTPException(status_code=403, detail="Admin access required")

        logger.info(f"Admin '{user.username}' authorized successfully")

        # Call the actual route function (handles sync and async)
        result = func(*args, **kwargs)
        return await result if inspect.isawaitable(result) else result

    return wrapper