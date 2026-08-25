from functools import wraps

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token

from config import Config
from models import User, db

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
jwt = JWTManager(app)
CORS(app)

with app.app_context():
    db.create_all()


def internal_only(fn):
    """Only admin-service (or anything holding the shared internal key) may call this."""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        provided_key = request.headers.get("X-Internal-Key")
        if provided_key != app.config["INTERNAL_SERVICE_KEY"]:
            return jsonify({"msg": "Forbidden: internal endpoint"}), 403
        return fn(*args, **kwargs)

    return wrapper


# ---------------- PUBLIC: REGISTER ----------------
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    if not data or not data.get("username") or not data.get("password"):
        return jsonify({"msg": "Username and password are required"}), 400

    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"msg": "User already exists"}), 400

    new_user = User(username=data["username"], role=data.get("role", "user"))
    new_user.set_password(data["password"])

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "User registered successfully"}), 201


# ---------------- PUBLIC: LOGIN ----------------
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data or not data.get("username") or not data.get("password"):
        return jsonify({"msg": "Username and password are required"}), 400

    user = User.query.filter_by(username=data["username"]).first()

    if not user or not user.check_password(data["password"]):
        return jsonify({"msg": "Invalid credentials"}), 401

    access_token = create_access_token(
        identity=user.username,
        additional_claims={"role": user.role},
    )

    return jsonify(access_token=access_token), 200


# ---------------- INTERNAL: used only by admin-service ----------------
@app.route("/internal/users", methods=["GET"])
@internal_only
def internal_list_users():
    users = User.query.all()
    return jsonify([u.to_dict() for u in users]), 200


@app.route("/internal/users/<int:user_id>", methods=["PUT"])
@internal_only
def internal_update_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    data = request.get_json() or {}
    user.username = data.get("username", user.username)
    user.role = data.get("role", user.role)
    db.session.commit()

    return jsonify(user.to_dict()), 200


@app.route("/internal/users/<int:user_id>", methods=["DELETE"])
@internal_only
def internal_delete_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({"msg": "User deleted successfully"}), 200


# ---------------- HEALTH CHECK ----------------
@app.route("/healthz", methods=["GET"])
def healthz():
    return jsonify({"status": "ok", "service": "auth-service"}), 200


if __name__ == "__main__":
    app.run(port=5000)
