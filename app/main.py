from fastapi import FastAPI
from app.db.session import engine, Base
from app.api.v1 import auth, reviews
from app.middleware.auth_middleware import JWTAuthMiddleware
from app.core.logger import logger 
from datetime import datetime
# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="User & Movie API")

# Include versioned API routers
app.include_router(auth.router, tags=["Auth"])
app.include_router(reviews.router , tags=["User reviews and ratings"])
app.add_middleware(JWTAuthMiddleware)

