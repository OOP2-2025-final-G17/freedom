from peewee import SqliteDatabase
from back_end.db.db import db, Schedule

MODELS = [
    Schedule,
]

def initialize_database():
    """Initialize database tables"""
    try:
        db.connect(reuse_if_open=True)
        db.create_tables(MODELS, safe=True)
        db.close()
    except Exception as e:
        print(f"Database initialization failed: {e}")
        raise