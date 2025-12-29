from app import create_app
from flask import g
from app.services.db import get_session
import os

app = create_app()

@app.before_request
def open_db():
    g.db = get_session()

@app.teardown_request
def close_db(exc):
    db = g.pop("db", None)
    if db:
        if exc:
            db.rollback()
        db.close()
        print(f"[DB] Session closed {id(db)}")

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8080")),
        debug=app.config.get("DEBUG", False),
    )
