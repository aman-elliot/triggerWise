from flask import request, jsonify
from flask_smorest import Blueprint, abort
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app.models import User
from app.schemas import UserSchema, UserRegistrationSchema, UserLoginSchema
from app import db
from flask import current_app

blp = Blueprint('users', 'users', description='Operations on users')

@blp.route('/register', methods=['POST'])
@blp.arguments(UserRegistrationSchema)
def register(user_data):
    """Register a new user."""
    try:
        email = user_data['email']
        password = user_data['password']

        if User.query.filter_by(email=email).first():
            return jsonify({"message": "User already exists"}), 400

        user = User(email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        user_registration_schema = UserRegistrationSchema()
        return jsonify(user_registration_schema.dump(user)), 201

    except Exception as e:
        # Log the error
        current_app.logger.error(f"Error during registration: {str(e)}")
        abort(500, message="An internal error occurred.")

@blp.route('/login', methods=['POST'])
@blp.arguments(UserLoginSchema)
def login(user_data):
    """Log in a user and issue access and refresh tokens."""
    try:
        email = user_data['email']
        password = user_data['password']

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            # Create access and refresh tokens
            access_token = create_access_token(identity=str(user.id))
            refresh_token = create_refresh_token(identity=str(user.id))

            return jsonify({
                "access_token": access_token,
                "refresh_token": refresh_token
            }), 200
        else:
            return jsonify({"message": "Invalid email or password"}), 401
    except Exception as e:
        # Log the error
        current_app.logger.error(f"Error during registration: {str(e)}")
        abort(500, message="An internal error occurred.")

@blp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)  # Only allow refresh tokens
def refresh():  
    """Issue a new access token using a refresh token."""
    current_user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user_id)
    return jsonify({"access_token": new_access_token}), 200

@blp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Log out the current user."""
    try:
        # In a stateless system, logout is handled by the frontend (discard tokens)
        return jsonify({"message": f"Logged out user."}), 200
    except Exception as e:
        # Log the error
        current_app.logger.error(f"Error during logout: {str(e)}")
        abort(500, message="An internal error occurred.")