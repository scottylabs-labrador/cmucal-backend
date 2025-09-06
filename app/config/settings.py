# Stores configuration like database URI, JWT secret key.
import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-jwt-secret")
    GOOGLE_CLIENT_SECRET_FILE = "client_secret.json"  # Google API credentials
    GOOGLE_SCOPES = ["https://www.googleapis.com/auth/calendar"]
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "your-google-client-id")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "your-google-client-secret")


