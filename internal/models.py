from internal.init import db
from sqlalchemy.orm import Mapped, mapped_column


class Movie(db.Model):
    __tablename__ = "movies"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    ratings = db.relationship("UserRating", back_populates="movie")


class UserRating(db.Model):
    __tablename__ = "user_ratings"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey("users.id"))
    movie_id: Mapped[int] = mapped_column(db.ForeignKey("movies.id"))
    rating: Mapped[int] = mapped_column(nullable=False)
    user = db.relationship("User", back_populates="ratings")
    movie = db.relationship("Movie", back_populates="ratings")


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, nullable=False)
    password = db.Column(db.String(32), nullable=False)
    # user_type is either 'user' or 'admin'
    user_type = db.Column(db.String(32), nullable=False)
    ratings = db.relationship("UserRating", back_populates="user")
