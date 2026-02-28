from flask import Flask, request
from flask_jwt_extended import JWTManager
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
jwt = JWTManager(app)

# Create database tables
from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt

def role_required(required_role):
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            claims = get_jwt()
            user_role = claims.get("role")

            if user_role != required_role:
                return jsonify({"msg": "Access forbidden: insufficient permissions"}), 403

            return fn(*args, **kwargs)
        return decorator
    return wrapper


# ---------------- REGISTER ----------------
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    # Validate input
    if not data or not data.get("username") or not data.get("password"):
        return jsonify({"msg": "Username and password are required"}), 400

    # Check if user exists
    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"msg": "User already exists"}), 400

    # Create new user (default role = user)
    new_user = User(
        username=data["username"],
        password=generate_password_hash(data["password"]),
        role=data.get("role", "user")
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "User registered successfully"}), 201


# ---------------- LOGIN ----------------
from flask_jwt_extended import create_access_token

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data or not data.get("username") or not data.get("password"):
        return jsonify({"msg": "Username and password are required"}), 400

    user = User.query.filter_by(username=data["username"]).first()

    if not user or not check_password_hash(user.password, data["password"]):
        return jsonify({"msg": "Invalid credentials"}), 401

    access_token = create_access_token(
        identity=user.username,                 # MUST be string
        additional_claims={"role": user.role}  # role goes here
    )

    return jsonify(access_token=access_token), 200


# ---------------- GET ALL USERS (Admin only) ----------------
@app.route("/users", methods=["GET"])
@role_required("admin")
def get_users():
    users = User.query.all()
    return jsonify([
        {
            "id": u.id,
            "username": u.username,
            "role": u.role
        }
        for u in users
    ]), 200


# ---------------- UPDATE USER ----------------
@app.route("/users/<int:id>", methods=["PUT"])
@role_required("admin")
def update_user(id):
    user = db.session.get(User, id)

    if not user:
        return jsonify({"msg": "User not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"msg": "No data provided"}), 400

    user.username = data.get("username", user.username)
    user.role = data.get("role", user.role)

    db.session.commit()

    return jsonify({"msg": "User updated successfully"}), 200


# ---------------- DELETE USER ----------------
@app.route("/users/<int:id>", methods=["DELETE"])
@role_required("admin")
def delete_user(id):
    user = db.session.get(User, id)

    if not user:
        return jsonify({"msg": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({"msg": "User deleted successfully"}), 200


if __name__ == "__main__":
    app.run(debug=True)