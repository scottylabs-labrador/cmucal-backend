# Initializes the Flask app, database, and JWT authentication.
import os
from dotenv import load_dotenv
from pathlib import Path
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

# Load environment variables from .env file BEFORE other imports
def detect_env() -> str:
    # Respect explicit setting (e.g., in Railway dashboard)
    app_env = os.getenv("APP_ENV")
    if app_env:
        return app_env.lower()

    # Heuristic: if we’re on Railway and APP_ENV isn’t set, assume production
    if os.getenv("RAILWAY_PROJECT_ID") or os.getenv("RAILWAY_ENVIRONMENT"):
        return "production"

    # Local default
    return "development"

ENV = detect_env()
print(f"[init] Detected APP_ENV={ENV}")
    
# Only load local .env files outside production
if ENV != "production":
    dotfile = f".env.{ENV}"
    if Path(dotfile).exists():
        load_dotenv(dotfile, override=False)

from app.config import DevelopmentConfig, TestingConfig, ProductionConfig
from app.services.db import SessionLocal, Base


def create_app():
    app = Flask(__name__)

    # honor X-Forwarded-* from Cloudflare/Railway
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)

    # HTTPS-aware defaults in prod
    if ENV == "production":
        app.config.from_object(ProductionConfig)
        app.config.update(
            PREFERRED_URL_SCHEME="https",
            SESSION_COOKIE_SECURE=True,
            REMEMBER_COOKIE_SECURE=True,
            # optional if you generate external URLs without _external/_scheme:
            # SERVER_NAME="api.cal.scottylabs.org",
        )
    elif ENV == "test":
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