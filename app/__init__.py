# Initializes the Flask app, database, and JWT authentication.
import os
from dotenv import load_dotenv
from pathlib import Path
from flask import Flask

# Load environment variables from .env file BEFORE other imports
env = (os.getenv("APP_ENV") or "development").lower()
load_dotenv(Path(f".env.{env}"), override=True)

from app.config import DevelopmentConfig, TestingConfig, ProductionConfig
from app.services.db import SessionLocal, Base


def create_app():
    app = Flask(__name__)


    if env == "production":
        app.config.from_object(ProductionConfig)
    elif env == "test":
        app.config.from_object(TestingConfig)
    else:
        app.config.from_object(DevelopmentConfig)

    if not os.getenv("ALEMBIC_RUNNING"): # skip during Alembic
        from flask_cors import CORS
        from app.api.users import users_bp
        from app.api.organizations import orgs_bp
        from app.api.base import base_bp
        from app.api.google import google_bp
        from app.api.events import events_bp
        from app.api.schedule import schedule_bp
        from app.cli import import_courses_command

        origins = [o.strip() for o in os.getenv(
            "CORS_ALLOWED_ORIGINS",
            "http://localhost:3000,https://cmucal.vercel.app,http://cmucal.com,https://cal.scottylabs.org"
        ).split(",")]
        

        CORS(app, resources={r"/api/*": {
            "origins": origins,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "Clerk-User-Id"],
        }}, supports_credentials=True)


        # Register blueprints (modular routing)
        app.register_blueprint(users_bp, url_prefix="/api/users")
        app.register_blueprint(orgs_bp, url_prefix="/api/organizations")
        app.register_blueprint(google_bp, url_prefix="/api/google")
        app.register_blueprint(events_bp, url_prefix="/api/events")
        app.register_blueprint(schedule_bp, url_prefix="/api/schedule")
        app.register_blueprint(base_bp)
        
        # Register CLI command
        app.cli.add_command(import_courses_command)

    return app