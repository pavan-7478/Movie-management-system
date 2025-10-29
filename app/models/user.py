from sqlalchemy import Column, Integer, String, Text, Float, Boolean, Enum, TIMESTAMP, ForeignKey, Date, BigInteger, text, CheckConstraint,UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.core.security import pwd_context
from app.db.session import engine 
# ----------------- User -----------------
class User(Base):
    __tablename__ = "User"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    role = Column(Enum('admin', 'user'), server_default='user')
    password = Column(String(255), nullable=False)
    status = Column(Enum('active', 'suspended'), server_default='active')
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), onupdate=text('CURRENT_TIMESTAMP'))

    # logins = relationship("UserLogins", back_populates="user", cascade="all, delete-orphan", passive_deletes=True)
    # movies_created = relationship("Movies", back_populates="creator", cascade="all, delete-orphan", passive_deletes=True)
    # reviews = relationship("Reviews", back_populates="user", cascade="all, delete-orphan", passive_deletes=True)
    # watchlist = relationship("Watchlist", back_populates="user", cascade="all,delete-orphan", passive_deletes=True)
    # activities = relationship("UserActivityLogs", back_populates="user", cascade="all, delete-orphan", passive_deletes=True)
    # recommendations = relationship("Recommendation", back_populates="user", cascade="all, delete-orphan", passive_deletes=True)

    def verify_password(self, plain_password: str) -> bool:
        return pwd_context.verify(plain_password, self.password)


# ----------------- User Logins -----------------
class UserLogins(Base):
    __tablename__ = "User_Logins"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(255), unique=True, nullable=False)
    status = Column(Enum('active', 'suspended'), server_default='active')
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    expiration_date = Column(TIMESTAMP)

    # user = relationship("User", back_populates="logins")


# ----------------- Movies -----------------
class Movies(Base):
    __tablename__ = "Movies"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    genre = Column(String(100))
    language = Column(String(50))
    director = Column(String(100))
    cast = Column(Text)
    release_year = Column(Integer)
    poster_url = Column(Text)
    rating = Column(Float, default=0.0)
    approved = Column(Boolean, default=False)
    created_by = Column(Integer, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), onupdate=text('CURRENT_TIMESTAMP'))

    # creator = relationship("User", back_populates="movies_created",cascade="all, delete-orphan", passive_deletes=True)
    # reviews = relationship("Reviews", back_populates="movie", cascade="all, delete-orphan", passive_deletes=True)
    # watchlist = relationship("Watchlist", back_populates="movie", cascade="all, delete-orphan", passive_deletes=True)
    # availability = relationship("MovieAvailability", back_populates="movie", cascade="all, delete-orphan", passive_deletes=True)
    # recommendations = relationship("Recommendation", back_populates="recommended_movie", cascade="all, delete-orphan", passive_deletes=True)


# ----------------- Reviews -----------------
class Reviews(Base):
    __tablename__ = "Reviews"

    id = Column(Integer, primary_key=True)
    movie_id = Column(Integer, ForeignKey("Movies.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    rating = Column(Float)
    comment = Column(Text)
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), onupdate=text('CURRENT_TIMESTAMP'))
    like_count= Column(Integer)
    sentiment_score= Column(Float)

    # movie = relationship("Movies", back_populates="reviews",cascade="all, delete-orphan", passive_deletes=True)
    # user = relationship("User", back_populates="reviews",cascade="all, delete-orphan", passive_deletes=True)

    __table_args__ = (
        UniqueConstraint("user_id", "movie_id", name="unique_user_movie_review"),
        CheckConstraint("rating >= 0 AND rating <= 10", name="rating_range_check"),
    )


#-----------------------Reviews Liked ones by a user ---------------
class Review_Liked(Base):
    __tablename__ = "Review_Liked"
    id = Column(Integer, primary_key=True)
    review_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    __table_args__ = (UniqueConstraint("review_id", "user_id", name="unique_review_user_like"),)


#----------------------History------------------
class ReviewHistory(Base):
    __tablename__ = "ReviewHistory"
    id = Column(Integer, primary_key=True)
    review_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
    old_rating = Column(Float)
    old_comment = Column(Text)
    changed_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))


# ----------------- Watchlist -----------------
class Watchlist(Base):
    __tablename__ = "Watchlist"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    movie_id = Column(Integer, ForeignKey("Movies.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))

    # user = relationship("User", back_populates="watchlist")
    # movie = relationship("Movies", back_populates="watchlist")


# ----------------- Platforms -----------------
class Platforms(Base):
    __tablename__ = "Platforms"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50))
    website = Column(Text)
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))

    # availability = relationship("MovieAvailability", back_populates="platform", cascade="all, delete-orphan", passive_deletes=True)


# ----------------- Regions -----------------
class Regions(Base):
    __tablename__ = "Regions"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True)
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))

    # availability = relationship("MovieAvailability", back_populates="region", cascade="all, delete-orphan", passive_deletes=True)


# ----------------- Movie Availability -----------------
class MovieAvailability(Base):
    __tablename__ = "Movie_Availability"

    id = Column(Integer, primary_key=True)
    movie_id = Column(Integer, ForeignKey("Movies.id", ondelete="CASCADE"), nullable=False)
    platform_id = Column(BigInteger, ForeignKey("Platforms.id", ondelete="CASCADE"), nullable=False)
    region_id = Column(BigInteger, ForeignKey("Regions.id", ondelete="CASCADE"), nullable=False)
    availability_type = Column(String(50))
    start_date = Column(Date)
    end_date = Column(Date)
    url = Column(Text)
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), onupdate=text('CURRENT_TIMESTAMP'))

    # movie = relationship("Movies", back_populates="availability")
    # platform = relationship("Platforms", back_populates="availability")
    # region = relationship("Regions", back_populates="availability")


# ----------------- User Activity Logs -----------------
class UserActivityLogs(Base):
    __tablename__ = "User_Activity_Logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    action_type = Column(String(100))
    description = Column(Text)
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))

    # user = relationship("User", back_populates="activities")


# ----------------- Recommendation -----------------
class Recommendation(Base):
    __tablename__ = "Recommendation"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    recommended_movie_id = Column(Integer, ForeignKey("Movies.id", ondelete="CASCADE"), nullable=False)
    reason = Column(Text)
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))

    # user = relationship("User", back_populates="recommendations")
    # recommended_movie = relationship("Movies", back_populates="recommendations")

Base.metadata.create_all(bind=engine)