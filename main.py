from flask import jsonify, request
import os
from werkzeug.utils import secure_filename
from internal.auth import generate_token, validate_token
from internal.models import Movie, UserRating, User
from internal.init import db, app, ALLOWED_EXTENSIONS


@app.route("/upload", methods=["POST"])
def upload_file():
    resp, code = validate_token(request, app.config["SECRET_KEY"])
    resp = resp.get_json()

    if "user" not in resp:
        return resp, code

    # Continue with the file upload process
    def allowed_file(filename):
        return (
            "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
        )

    if request.method != "POST":
        return jsonify({"message": "Method not allowed"}), 405

    if "file" not in request.files:
        return jsonify({"message": "No file part"}), 400

    if not os.path.exists(app.config["UPLOAD_FOLDER"]):
        os.makedirs(app.config["UPLOAD_FOLDER"])

    successful_uploads = []

    # Upload any valid files. Stop uploading if an invalid file is found
    for file in request.files.getlist("file"):
        if not file.filename or file.filename == "":
            return (
                jsonify(
                    {
                        "message": "No selected file",
                        "successful_uploads": successful_uploads,
                    }
                ),
                400,
            )

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            successful_uploads.append(filename)
        else:
            return (
                jsonify(
                    {
                        "message": "Invalid file type",
                        "filename": file.filename,
                        "successful_uploads": successful_uploads,
                    }
                ),
                415,
            )

    return (
        jsonify(
            {
                "message": "Files uploaded successfully",
                "successful_uploads": successful_uploads,
            }
        ),
        200,
    )

# Registration endpoint for user sign-up
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

    user = User(username=username, password=password, user_type="user")

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
@app.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    username, password = data.get("username"), data.get("password")

    if not username or not password:
        return jsonify({"message": "Username and password are required"}), 400

    user = User.query.filter_by(username=username, password=password).first()
    if not user:
        return jsonify({"message": "Invalid credentials"}), 401

    token = generate_token(app.config["SECRET_KEY"])
    if not token:
        return jsonify({"message": "Unable to create token", "token": None}), 400

    return jsonify({"message": "Login Success", "token": token}), 200


# Endpoint for admins to add a new movie to the database
@app.route("/admin/add-movie", methods=["POST"])
def admin_add_movie():
    resp, code = validate_token(request, app.config["SECRET_KEY"])
    resp = resp.get_json()

    # If the user exists in resp, the token is valid
    if "user" not in resp:
        return resp, code

    username = resp.get("user")
    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({"message": "User not found"}), 404

    user_type = user.user_type
    if user_type != "admin":
        return jsonify({"message": "Unauthorized"}), 401

    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    if "title" not in data:
        return jsonify({"error": "Title is required"}), 400

    # Check if the movie already exists
    movie = Movie.query.filter_by(title=data["title"]).first()
    if movie:
        return jsonify({"message": "Movie already exists"}), 400

    movie = Movie(title=data["title"])

    try:
        db.session.add(movie)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Unable to create a movie.", "error": str(e)}), 400

    finally:
        db.session.close()

    return (
        jsonify(
            {
                "message": f"Movie created successfully: {data.get('title')}",
                "error": None,
            }
        ),
        200,
    )


# An endpoint for users to submit their ratings for movies
@app.route("/add-rating/<int:movie_id>", methods=["POST"])
def add_rating(movie_id):
    resp, code = validate_token(request, app.config["SECRET_KEY"])
    resp = resp.get_json()

    if "user" not in resp:
        return resp, code

    username = resp["user"]
    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({"message": "User not found"}), 404

    # Admins can't rate movies
    if not user.user_type or user.user_type == "admin":
        return jsonify({"message": "Unauthorized"}), 401

    data = request.get_json()
    rating = data.get("rating")

    if not rating or not (1 <= rating <= 5):
        return jsonify({"message": "Rating must be between 1 and 5"}), 400

    movie = Movie.query.get(movie_id)
    if not movie:
        return jsonify({"message": "Movie not found"}), 404

    user_rating = UserRating(user_id=user.id, movie_id=movie.id, rating=rating)

    try:
        db.session.add(user_rating)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Unable to add rating.", "error": str(e)}), 400

    return jsonify({"message": "Rating addded successfully"}), 200


# Endpoint to retrieve a list of existing user ratings for all movies
@app.route("/movies", methods=["GET"])
def get_movies():
    movies = Movie.query.all()

    if not movies:
        return jsonify({"message": "No movies found"}), 404

    res = []
    for movie in movies:
        res.append({"id": movie.id, "title": movie.title})

    return jsonify(res), 200


# Endpoint to fetch details for a specific movie, including its user ratings
@app.route("/movies/<int:movie_id>", methods=["GET"])
def get_movie_details(movie_id):
    movie = Movie.query.get(movie_id)

    if not movie:
        return jsonify({"message": "Movie not found"}), 404

    ratings = [
        {"user_id": rating.user_id, "rating": rating.rating, "rating_id": rating.id}
        for rating in movie.ratings
    ]
    return jsonify({"id": movie.id, "title": movie.title, "ratings": ratings}), 200


# Endpoint that allows users to update their own movie ratings
@app.route("/update-rating/<int:movie_id>", methods=["PUT"])
def update_rating(movie_id):
    resp, code = validate_token(request, app.config["SECRET_KEY"])
    resp = resp.get_json()

    if "user" not in resp:
        return resp, code

    username = resp["user"]
    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({"message": "User not found"}), 404

    data = request.get_json()
    new_rating = data.get("rating")

    if not new_rating or not (1 <= new_rating <= 5):
        return jsonify({"message": "Rating must be between 1 and 5"}), 400

    rating = UserRating.query.filter_by(user_id=user.id, movie_id=movie_id).first()

    if not rating:
        return jsonify({"message": "Rating not found"}), 404

    rating.rating = new_rating

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Unable to update rating.", "error": str(e)}), 400

    return jsonify({"message": "Rating updated successfully"}), 200


# Admins can delete any rating
@app.route("/admin/delete-rating/<int:rating_id>", methods=["DELETE"])
def admin_delete_rating(rating_id):
    resp, code = validate_token(request, app.config["SECRET_KEY"])
    resp = resp.get_json()

    if "user" not in resp:
        return resp, code

    username = resp["user"]
    user = User.query.filter_by(username=username).first()

    if not user or user.user_type != "admin":
        return jsonify({"message": "Unauthorized"}), 401

    rating = UserRating.query.get(rating_id)

    if not rating:
        return jsonify({"message": "Rating not found"}), 404

    try:
        db.session.delete(rating)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Unable to delete rating.", "error": str(e)}), 400

    return jsonify({"message": "Rating deleted successfully"}), 200


# user can delete their own rating from a particular movie
@app.route("/delete-rating/<int:movie_id>", methods=["DELETE"])
def delete_user_rating(movie_id):
    resp, code = validate_token(request, app.config["SECRET_KEY"])
    resp = resp.get_json()

    if "user" not in resp:
        return resp, code

    username = resp["user"]
    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({"message": "User not found"}), 404

    rating = UserRating.query.filter_by(user_id=user.id, movie_id=movie_id).first()
    if not rating:
        return jsonify({"message": "Rating not found"}), 404

    try:
        db.session.delete(rating)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Unable to delete rating.", "error": str(e)}), 400

    return jsonify({"message": "Rating deleted successfully"}), 200


if __name__ == "__main__":
    # Create the DB tables if they don't exist
    with app.app_context():
        db.create_all()

    app.run(debug=True, port=4444)
