# Stores configuration like database URI, JWT secret key.
import os

class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-jwt-secret")
    
    GOOGLE_CLIENT_SECRET_FILE = "client_secret.json"  # Google API credentials
    GOOGLE_SCOPES = ["https://www.googleapis.com/auth/calendar"]
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "your-google-client-id")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "your-google-client-secret")

    GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
    FRONTEND_REDIRECT_URI = os.getenv("FRONTEND_REDIRECT_URI")

    SQLALCHEMY_DATABASE_URI = os.getenv("SUPABASE_DB_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")
    SUPABASE_DB_URL = os.getenv("SUPABASE_DB_URL")

    TESTING = False
    DEBUG = False

class DevelopmentConfig(BaseConfig):
    DEBUG = True

class TestingConfig(BaseConfig):
    TESTING = True

class ProductionConfig(BaseConfig):
    pass


