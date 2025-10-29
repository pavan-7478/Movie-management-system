from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.reviews import ReviewCreate, ReviewUpdate, ReviewOut, PaginatedReviews
from app.services.user_reviews import add_review, update_review, delete_review, list_reviews_by_movie, like_review
from app.core.logger import logger
from typing import Optional
from datetime import datetime
from app.utils.decorators import admin_required, login_required

router = APIRouter(prefix="/user")
security = HTTPBearer()

def _get_user_from_request(request: Request):
    return getattr(request.state, "user", None)


@router.post("/reviews", status_code=status.HTTP_201_CREATED, dependencies=[Depends(security)])
@login_required
def create_review(request: Request, payload: ReviewCreate, db: Session = Depends(get_db)):
    logger.info({
        "message":"Create review route accessed",
        "timestamp":datetime.now().isoformat()
    })
    user = _get_user_from_request(request)
    review = add_review(db, user_id=user.id, movie_id=payload.movie_id, rating=payload.rating, comment=payload.comment)
    logger.info({
        "message":"Create review successful",
        "timestamp":datetime.now().isoformat()
    })
    return review


@router.get("/reviews/by-movie/{movie_id}",dependencies=[Depends(security)])
def get_reviews(movie_id: int, page: int = 1, size: int = 10, ratingFrom: float = 0.0, userId: Optional[int] = None, sort: str = "created_at", order: str = "desc", db: Session = Depends(get_db)):
    logger.info({
        "message":"Get reviews by movie-id route accessed",
        "timestamp":datetime.now().isoformat()
    })
    result = list_reviews_by_movie(db, movie_id=movie_id, page=page, size=size, ratingFrom=ratingFrom, userId=userId, sort=sort, order=order)
    return result


@router.put("/reviews/{review_id}",status_code=status.HTTP_200_OK,dependencies=[Depends(security)])
@admin_required
def modify_review(request: Request, review_id: int, payload: ReviewUpdate, db: Session = Depends(get_db)):
    logger.info({
        "message":"Update review route accessed",
        "timestamp":datetime.now().isoformat()
    })
    user = _get_user_from_request(request)
    updated = update_review(db, review_id=review_id, user_id=user.id, rating=payload.rating, comment=payload.comment)
    
    return {
        "user_id":updated.user_id,
         "movie_id":updated.movie_id,
         "comment": updated.comment,
         "rating": updated.rating
          }


@router.delete("/reviews/{review_id}", status_code=status.HTTP_200_OK,dependencies=[Depends(security)])
@admin_required
def remove_review(request:Request, review_id: int, user_id:int, db: Session = Depends(get_db)):
    logger.info({
        "message":"Delete review route accessed",
        "timestamp":datetime.now().isoformat()
    })
    if delete_review(db, review_id=review_id, user_id=user_id):
         return {"message":"Successfully user deleted"}


@router.post("/reviews/{review_id}/like",dependencies=[Depends(security)])
def like_a_review(request: Request, review_id: int, db: Session = Depends(get_db)):
    logger.info({
        "message":"Like a review route accessed",
        "timestamp":datetime.now().isoformat()
    })
    user = _get_user_from_request(request)
    return like_review(db, review_id=review_id, user_id=user.id)


# admin access to remove the review
# @router.delete("/reviews/{review_id}/admin", status_code=status.HTTP_204_NO_CONTENT,dependencies=[Depends(security)])
# @admin_required
# def admin_remove_review(request: Request, review_id: int, db: Session = Depends(get_db)):
#     admin = _get_user_from_request(request)
#     admin_delete_review(db, review_id=review_id, admin_user_id=admin.user_id)
#     logger.info({
#         "message":"Successfully performed operation",
#         "timestamp":datetime.now().isoformat()
#     })
#     return {"message":"Admin accessed and review removed successfully"}

