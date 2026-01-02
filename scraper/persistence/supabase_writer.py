# scraper/persistence/supabase_writer.py
from supabase import create_client, Client
import os

_supabase: Client | None = None


def get_supabase() -> Client:
    global _supabase
    if _supabase is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

        if not url or not key:
            raise RuntimeError("Supabase env vars not set")
        _supabase = create_client(url, key)
    return _supabase
