from flask import Flask
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_smorest import Api

from app.logger import setup_logger
from app.routes import register_routes
from .config import Config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    # Set up the logger once and assign it to app.logger
    setup_logger(app)
    
    # Now you can use app.logger throughout your app
    app.logger.info("Flask app initialized!")

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    register_routes(app)
    
    return app
