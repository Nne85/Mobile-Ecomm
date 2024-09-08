from flask import Blueprint, request, jsonify, abort
from app import db
from app.models.user import User
from app.models.blacklist import TokenBlacklist
from flask_jwt_extended import (
        create_access_token, create_refresh_token, jwt_required,
        get_jwt_identity, get_jwt, JWTManager
)

bp = Blueprint('auth', __name__, url_prefix='/users')
jwt = JWTManager()

@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    token = TokenBlacklist.query.filter_by(jti=jti).first()
    return token is not None


@bp.route('/register', methods=['POST'])
def register():
    """ Register a new user """
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({"error": "Username, email, and password are required"}), 400

    errors = []
    try:
        User.validate_email(email)
    except ValueError as e:
        errors.append({'field': 'email', 'message': str(e)})

    if len(password) < 8:
        errors.append({'field': 'password', 'message': "Password must be at least 8 characters long"})

    if db.session.query(User).filter_by(username=username).first():
        errors.append({'field': 'username', 'message': "Username already exists"})

    if errors:
        return jsonify({'message': 'Validation errors', 'errors': errors}), 400

    try:
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        return jsonify({"error": "User registration failed"}), 500


@bp.route('/login', methods=['POST'])
def login():
    """ Login a user """
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = db.session.query(User).filter_by(email=email).first()

    if user is None or not user.check_password(password):
        return jsonify({'message': 'Invalid email or password'}), 401
    
    access_token = create_access_token(identity=user.id)
    return jsonify({'message': 'Login successful', 'access_token': access_token}), 200 


@bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """ Logout a user """
    jti = get_jwt()['jti']
    try:
        blacklisted_token = TokenBlacklist(jti=jti)
        db.session.add(blacklisted_token)
        db.session.commit()
        return jsonify({'message': 'Logged out successfully'}), 200
    except Exception as e:
        return jsonify({"error": "Failed to log out"}), 500

@bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    """ Get user profile details """
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_admin": user.is_admin,
        "created_at": user.created_at
    }), 200


@bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """ Retrieve a specific user account by ID """
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_admin": user.is_admin,
        "created_at": user.created_at
    }), 200


@bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """ Update an existing user account """
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    if get_jwt_identity() != user.id:
        return jsonify({"error": "You do not have permission to update this user"}), 403

    data = request.get_json()
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)

    if 'password' in data:
        user.set_password(data['password'])
    try:
        User.validate_email(user.email)
        db.session.commit()
        return jsonify({"message": "User updated successfully"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Failed to update user"}), 500



@bp.route('/reset-password', methods=['POST'])
def reset_password():
    """ Resets Password"""
    email = request.args.get('email')
    if not email:
        return jsonify({"error": "Email is required"}), 400

    user = db.session.query(User).filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Invalid email"}), 404

    return jsonify({"message": f"Password reset instructions sent to {email}"}), 200



@bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """ Deletes a user account"""
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    if get_jwt_identity() != user.id and not get_jwt_identity().is_admin:
        return jsonify({"error": "You do not have permission to delete this user"}), 403

    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "User deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": "Failed to delete user"}), 500
