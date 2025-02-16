import os
from dotenv import load_dotenv
from datetime import timedelta
load_dotenv()  # Load environment variables

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    RQ_REDIS_URL = os.getenv("REDIS_URL")
    API_TITLE = "Event Trigger API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.2"
    OPENAPI_URL_PREFIX = "/"
    OPENAPI_SWAGGER_UI_PATH = "/swagger-ui"
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')  # Default to 'production' if FLASK_ENV is not set
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super-secret-key")  # Change this in production
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)  # Access token expires in 15 minutes
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)     # Refresh token expires in 7 days
    JWT_TOKEN_LOCATION = ["headers"]       # Allow tokens in headers or cookies
    JWT_COOKIE_SECURE = False                         # Set to True in production (HTTPS only)
    JWT_COOKIE_CSRF_PROTECT = True                    # Enable CSRF protection for cookies