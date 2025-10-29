from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.security import JWTManager
from app.db.session import SessionLocal
from app.models.user import User
 
 
class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Public (unauthenticated) routes
        public_routes = [
            "/auth/login",
            "/auth/register",
             "/openapi.json",
            "/docs",
            "/redoc"
        ]
        if any(request.url.path.startswith(route) for route in public_routes):
            return await call_next(request)
 
        # Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing or invalid Authorization header"},
            )
 
        token = auth_header.split(" ")[1]
 
        # Verify JWT
        payload = JWTManager.verify_jwt(token)
        if not payload:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid or expired token"},
            )
 
        # Fetch user from DB
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == payload.get("user_id")).first()
            request.state.user = user
        finally:
            db.close()
 
        if not user:
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "User not found"})
        
        # we should even make sure that the user is sctive currently
        if user.status == "suspended":
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail":"User is not accessesd"})
        # Attach user to request (accessible in routes)
 
        response = await call_next(request)
        return response
 
 