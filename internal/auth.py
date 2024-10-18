from flask import jsonify, request, Request
import datetime
import jwt


def generate_token(secret_key):
    data = request.get_json()
    username = data.get("username")
    if not username:
        return None

    expire_at = datetime.datetime.now() + datetime.timedelta(minutes=30)
    payload = {"username": username, "expire_at": str(expire_at)}

    token = jwt.encode(payload=payload, key=secret_key, algorithm="HS256")
    return token


def validate_token(request: Request, secret_key):
    token = request.headers.get("Authorization")

    if not token:
        return jsonify({"message": "Token is missing"}), 400

    # Extract token from 'Bearer <token>' format if present
    try:
        token = token.split(" ")[1]
    except Exception:
        return jsonify({"message": "Invalid token format"}), 400

    try:
        decoded = jwt.decode(token, secret_key, algorithms=["HS256"])
        return jsonify({"message": "Token is valid", "user": decoded["username"]}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Token has expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "Invalid token"}), 401
