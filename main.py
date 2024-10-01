from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


load_dotenv()


def get_env_var(env_var):
    try:
        return os.getenv(env_var)
    except KeyError:
        raise Exception(f"{env_var} not found in your .env file!")


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = get_env_var("DATABASE_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app, model_class=Base)


class Movie(db.Model):
    __tablename__ = "movies"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    ratings = db.relationship("UserRating", backref="movie")


class UserRating(db.Model):
    __tablename__ = "user_ratings"
    user_id: Mapped[int] = mapped_column(primary_key=True)
    movie_id: Mapped[int] = mapped_column(primary_key=True)
    rating: Mapped[int] = mapped_column(nullable=False)


# Registration endpoint for user sign-up
@app.route("/auth/signup", methods=["POST"])
def signup():
    return "Sign Up", 200


# Login endpoint to authenticate users
@app.route("/auth/login", methods=["POST"])
def login():
    return "Log In", 200


# Endpoint for admins to add a new movie to the database
@app.route("/admin/add-movie", methods=["POST"])
def admin_add_movie():
    return "Add Movie", 200


# An endpoint for users to submit their ratings for movies
@app.route("/add-rating/<movie>")
def add_rating():
    return "Add Movie Rating", 200


# Endpoint to retrieve a list of existing user ratings for all movies
@app.route("/movies", methods=["GET"])
def get_movies():
    return "All Movies", 200


# Endpoint to fetch details for a specific movie, including its user ratings
@app.route("/movies/<movie>", methods=["GET"])
def get_movie_details():
    return "Movie Details", 200


# Endpoint that allows users to update their own movie ratings
@app.route("/update-rating/<movie>", methods=["PUT"])
def update_rating():
    return "Update User Rating", 200


# Admin-only endpoint to delete any movie's user rating from the database
@app.route("/admin/delete-rating", methods=["DELETE"])
def admin_delete_rating():
    return "Delete Rating", 200


# Endpoint for users to delete their own ratings
@app.route("/delete-rating", methods=["DELETE"])
def delete_user_rating():
    return "Delete Rating", 200


if __name__ == "__main__":
    app.run(debug=True)
