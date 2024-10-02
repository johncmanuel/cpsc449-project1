from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
import datetime
import jwt

load_dotenv()

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("SQLALCHEMY_DATABASE_URI")

db = SQLAlchemy(app)

class User(db.Model):
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
@app.route("/auth/signup", methods=["POST"])
def signup():
    return "Sign Up", 200


# Login endpoint to authenticate users
@app.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    return jsonify({ "message": "Login Success" }), 200


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
