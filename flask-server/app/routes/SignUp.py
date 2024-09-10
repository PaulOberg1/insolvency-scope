from flask import Flask, request, jsonify, Blueprint
from flask_jwt_extended import create_access_token, JWTManager
from .. import User
from sqlalchemy.exc import IntegrityError

# Define new Blueprint "SignUpBP" to register in __init__.py
bp = Blueprint("SignUpBP",__name__)

@bp.route("/signup", methods=["POST"])
def signup():
    """
    Route to create a new user account and issue a JWT token.
    Expected JSON input format:
    {
        "username": string,
        "password": string
    }

    Returns:
        JSON response containing jwt token if credentials are valid,
        otherwise an error message.
    """
    try:
        #Retrieve db object for database entries, and bcrypt object for hashing
        from .. import db, bcrypt

        #Extract username and password from incoming JSON request
        data = request.json
        username = data["username"]
        password = data["password"]

        #Hash the extracted password
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

        #Create a new user with username and hashed password, and add it to database
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        #Generate a JWT access token with the username as the identity
        access_token = create_access_token(identity=username)

        #Return the access token in the response with status code 200
        return jsonify({"access_token": access_token}), 200
    except IntegrityError as e:
        # Handle case where a unique constraint (e.g., username) is violated
        db.session.rollback()
        return jsonify({"message": "Username already exists"}), 400
    except Exception as e:
        #Catch exceptions in the route and return a corresponding error message
        return jsonify({"message": f"Signup failure: {e}"}), 500
