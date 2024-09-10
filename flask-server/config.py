class Config:
    """
    Configuration class for Flask application settings.

    Attributes:
        SQLALCHEMY_DATABASE_URI (str): URI for connecting to the MySQL database.
        SQLALCHEMY_TRACK_MODIFICATIONS (bool): Disable modification tracking to avoid overhead.
        SECRET_KEY (str): Secret key for session management and security features.
        JWT_SECRET_KEY (str): Secret key for encoding and decoding JSON Web Tokens (JWTs).
    """
    
    # URI for connecting to the MySQL database
    SQLALCHEMY_DATABASE_URI = 'mysql://root:orange1931@127.0.0.1/login_db'
    # Disable Flask-SQLAlchemy's event system to reduce overhead
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Secret key used for session management, encryption, and CSRF protection
    SECRET_KEY = '125'
    # Secret key used for signing JWTs (JSON Web Tokens) for authentication
    JWT_SECRET_KEY = '125'
