from pydantic import BaseModel, EmailStr, conint, constr
from typing import Optional, List 
from datetime import datetime 
# ----------------- User Create -----------------
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    role: Optional[str] = "user"
    password: str

# ----------------- User Login -----------------
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# ----------------- User Response -----------------
class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str
    status: str
    created_at: str

    class Config:
        orm_mode = True

#-------------------- User review and rating required pydantic schemas-----------------

# class ReviewCreate(BaseModel):
#     movie_id: int
#     rating: conint(ge=0, le=10)
#     comment: Optional[constr(strip_whitespace=True, max_length=2000)] = None

# class ReviewUpdate(BaseModel):
#     rating: Optional[conint(ge=0, le=10)] = None
#     comment: Optional[constr(strip_whitespace=True, max_length=2000)] = None

# class ReviewOut(BaseModel):
#     id: int
#     movie_id: int
#     user_id: int
#     rating: float
#     comment: Optional[str]
#     like_count: int
#     sentiment_score: Optional[float]
#     created_at: datetime
#     updated_at: Optional[datetime]

#     class Config:
#         orm_mode = True

# class PaginatedReviews(BaseModel):
#     total: int
#     page: int
#     size: int
#     reviews: List[ReviewOut]
