from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
import datetime
import jwt
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

app.config["SECRET_KEY"] = get_env_var("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = get_env_var("DATABASE_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app, model_class=Base)


class Movie(db.Model):
    __tablename__ = "movies"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    # Triggers a foreign key error when testing to create movies, so leaving it out for now
    # ratings = db.relationship("UserRating", backref="Movie", lazy=True)


class UserRating(db.Model):
    __tablename__ = "user_ratings"
    user_id: Mapped[int] = mapped_column(primary_key=True)
    movie_id: Mapped[int] = mapped_column(primary_key=True)
    rating: Mapped[int] = mapped_column(nullable=False)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, nullable=False)
    password = db.Column(db.String(32), nullable=False)


def generate_token():
    data = request.get_json()
    username = data.get("username")
    if not username:
        return jsonify({"message": "Username not provided"}), 400

    expire_at = datetime.datetime.now() + datetime.timedelta(minutes=30)

    payload = {"username": username, "expire_at": expire_at}

    token = jwt.encode(payload=payload, key=app.config["SECRET_KEY"], algorithm="HS256")
    return jsonify({"token": token}), 200


def validate_token():
    token = request.headers.get("Authentication")
    if not token:
        return jsonify({"message": "Token is missing"}), 400

    # Extract token from 'Bearer <token>' format if present
    try:
        token = token.split(" ")[1]
    except:
        return jsonify({"message": "Invalid token format"}), 400

    try:
        decoded = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
        return jsonify({"message": "Token is valid", "user": decoded["username"]}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Token has expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "Invalid token"}), 401


# Registration endpoint for user sign-up
# TODO: Add JWT token generation
@app.route("/auth/signup", methods=["POST"])
def signup():
    data = request.get_json()
    username, password = data.get("username"), data.get("password")

    if not username or not password:
        return jsonify({"message": "Username and password are required"}), 400

    # Check if the user already exists
    user = User.query.filter_by(username=username).first()
    if user:
        return jsonify({"message": "User already exists"}), 400

    user = User(username=username, password=password)

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error creating a user.", "error": str(e)}), 400
    finally:
        db.session.close()

    return jsonify({"message": "User created successfully", "error": None}), 200


# Login endpoint to authenticate users
# TODO: Validate JWT token, check hashed passwords, and add other security stuff
@app.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    username, password = data.get("username"), data.get("password")

    if not username or not password:
        return jsonify({"message": "Username and password are required"}), 400

    user = User.query.filter_by(username=username, password=password).first()
    if not user:
        return jsonify({"message": "Invalid credentials"}), 401

    return jsonify({"message": "Login Success"}), 200


# Endpoint for admins to add a new movie to the database
@app.route("/admin/add-movie", methods=["POST"])
def admin_add_movie():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    if "title" not in data:
        return jsonify({"error": "Title is required"}), 400

    movie = Movie(title=data["title"])

    try:
        db.session.add(movie)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Unable to create a movie.", "error": str(e)}), 400

    finally:
        db.session.close()

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
    # Create the DB tables if they don't exist
    with app.app_context():
        db.create_all()

    app.run(debug=True)
