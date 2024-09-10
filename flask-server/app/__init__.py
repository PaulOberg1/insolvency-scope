from flask import Flask, jsonify, render_template, request, session, Response, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import create_access_token, JWTManager
import redis
from config import Config

#Instantiate relevant classes for integration in Flask application
db = SQLAlchemy() #Database object for database queries
bcrypt = Bcrypt() #Bcrypt object for password hashing
jwt = JWTManager() #JWT object for secutiry
cors = CORS() #CORS object to enable CORS
r = redis.Redis(host='localhost', port=6379, db=0) #Redis object for server-side storage

#Create database model "User"
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True) #Primary key uniquely identifying each row
    username = db.Column(db.String(80), unique=True, nullable=False) #Mandatory username field, must be unique from all other usernames
    password = db.Column(db.String(80), nullable=False) #Mandatory password fiel

def createApp():
    """
    Configures, initialises and returns a Flask application object.

    Returns:
        The Flask application object.

    """

    #Create Flask app, specifying directories for static content and templates
    app = Flask(__name__, static_folder='static',template_folder="templates")

    #Set up app configuration using details specified in Config class
    app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = Config.SQLALCHEMY_TRACK_MODIFICATIONS
    app.config['SECRET_KEY'] = Config.SECRET_KEY
    app.config['JWT_SECRET_KEY'] = Config.JWT_SECRET_KEY

    #Initialise app with relevant abilities enabled
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)

    #Initialise database
    with app.app_context():
        db.create_all()

    #Access blueprints from "routes" directory
    from app.routes.GetInstructions import bp as GetInstructionsBP
    from app.routes.LogIn import bp as LogInBP
    from app.routes.RenderMap import bp as RenderMapBP
    from app.routes.SignUp import bp as SignUpBP
    from app.routes.LogOut import bp as LogOutBP

    #Register all blueprints with central Flask app
    for bp in ([GetInstructionsBP,LogInBP,RenderMapBP,SignUpBP,LogOutBP]):
        app.register_blueprint(bp)

    #Return Flask app
    return app
    


