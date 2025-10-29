"""
This contains all the required functions for rating calculation and updating
the db simultaneously
"""
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.models.user import Reviews, Movies, Review_Liked
from app.core.logger import logger
from typing import Optional
def _sentiment_placeholder(text: str): 
    if not text:
        return None
    txt = text.lower()
    pos = sum(word in txt for word in ("good","great","amazing","love","excellent","enjoyed"))
    neg = sum(word in txt for word in ("bad","boring","terrible","awful","hate","worst"))
    score = (pos - neg) / (pos + neg + 1e-6)
    return max(0.0, min(1.0, (score + 1) / 2))

def recalc_movie_rating(db: Session, movie_id: int):
    avg = db.query(func.avg(Reviews.rating)).filter(Reviews.movie_id == movie_id).scalar()
    avg_val = float(avg) if avg is not None else 0.0
    movie = db.query(Movies).filter(Movies.id == movie_id).first()
    if movie:
        movie.rating = avg_val
        db.add(movie)
        db.commit()
        logger.info("Recalculated movie %s rating -> %s",movie_id ,avg_val)
    return avg_val

def add_review(db: Session, user_id: int, movie_id: int, rating: float, comment: str):
    # check movie exists
    movie = db.query(Movies).filter(Movies.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    print("user_id", user_id, "movie_id", movie_id)
    existing = db.query(Reviews).filter((Reviews.user_id == user_id) and (Reviews.movie_id == movie_id)).first()
    print(existing, "88888")
    if existing:
        raise HTTPException(status_code=400, detail="You already reviewed this movie")
    sentiment = _sentiment_placeholder(comment)
    review = Reviews(movie_id=movie_id, user_id=user_id, rating=float(rating), comment=comment,sentiment_score=sentiment)
    db.add(review)
    db.commit()
    db.refresh(review)
    recalc_movie_rating(db, movie_id)
    logger.info("Review %s created by user %s for movie %s",review.id, user_id ,movie_id)
    return review

def update_review(db: Session, review_id: int, user_id: int, rating: float, comment: str):
    review = db.query(Reviews).filter(Reviews.id == review_id, Reviews.user_id == user_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
 
    if rating is not None:
        review.rating = float(rating)
    if comment is not None:
        review.comment = comment
        review.sentiment_score = _sentiment_placeholder(comment)
    db.add(review)
    db.commit()
    db.refresh(review)
    recalc_movie_rating(db, review.movie_id)
    logger.info("Review %s updated by user %s", review_id, user_id)
    return review

def delete_review(db: Session, review_id: int, user_id: int):
    review = db.query(Reviews).filter(Reviews.id == review_id, Reviews.user_id == user_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    movie_id = review.movie_id
    db.delete(review)
    db.commit()
    db.expire_all()
    recalc_movie_rating(db, movie_id)
    logger.info("Review %s deleted by user %s", review_id, user_id)
   
    return True

# def admin_delete_review(db: Session, review_id: int, admin_user_id: int):
#     review = db.query(Reviews).filter(Reviews.id == review_id).first()
#     if not review:
#         raise HTTPException(status_code=404, detail="Review not found")
#     movie_id = review.movie_id
#     db.delete(review)
#     db.commit()
#     recalc_movie_rating(db, movie_id)
#     logger.info("Admin %s deleted review %s",admin_user_id, review_id)
#     return {"message": "Review deleted by admin"}

def list_reviews_by_movie(db: Session, movie_id: int, page: int = 1, size: int = 10, ratingFrom: float = 0.0, 
    userId: Optional[int] = None, sort: str = "created_at", order: str = "desc"):
    q = db.query(Reviews).filter(Reviews.movie_id == movie_id)
    if ratingFrom:
        q = q.filter(Reviews.rating >= ratingFrom)
    if userId:
        q = q.filter(Reviews.user_id == userId)
    total = q.count()
    # sort
    if sort == "helpful":
        order_col = Reviews.like_count
    else:
        order_col = getattr(Reviews, sort, Reviews.created_at)
    if order.lower() == "desc":
        q = q.order_by(desc(order_col))
    else:
        q = q.order_by(order_col)
    reviews = q.offset((page - 1) * size).limit(size).all()
    return {"total": total, "page": page, "size": size, "reviews": reviews}

def like_review(db: Session, review_id: int, user_id: int):
    review = db.query(Reviews).filter(Reviews.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    exists = db.query(Review_Liked).filter(Review_Liked.review_id == review_id, Review_Liked.user_id == user_id).first()
    if exists:
        logger.info("User %s already liked review %s", user_id, review_id)
        return {"message": "Already liked", "like_count": review.like_count}
    like = Review_Liked(review_id=review_id, user_id=user_id)
    db.add(like)
    review.like_count = (review.like_count or 0) + 1
    db.add(review)
    db.commit()
    db.refresh(review)
    logger.info("User %s liked review %s", user_id, review_id)
    return {"message": "Review liked", "like_count": review.like_count}
