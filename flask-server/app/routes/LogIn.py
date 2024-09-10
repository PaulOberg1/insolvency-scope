from flask import Flask, request, jsonify, Blueprint
from flask_jwt_extended import create_access_token, JWTManager
from .. import User

# Define new Blueprint "LogInBP" to register in __init__.py
bp = Blueprint("LogInBP",__name__)

@bp.route("/login",methods=["POST"])
def login():
    """
    Route to handle user login credentials and issue a JWT token.
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
        #Import bcrypt object to manage hashing
        from .. import bcrypt

        #Extract username and password from the incoming JSON request
        data = request.json
        username,password = data["username"],data["password"]

        #Query the database for a user with the given username
        user = User.query.filter_by(username=username).first()

        # Check if the user exists and the provided password matches the stored hash
        if user and bcrypt.check_password_hash(user.password, password):
            # Generate a JWT access token with the username as the identity
            access_token = create_access_token(identity=username)
            # Return the access token in the response with a 200 status code
            return jsonify({"access_token": access_token}), 200
        else:
            #Return error message indicating invalid login credentials
            return jsonify({"message":"login failure"}), 401
    except Exception as e:
        #Catch exceptions in the route and return the corresponding message to the frontend
        return jsonify({"message":"failure logging in"}), 500

