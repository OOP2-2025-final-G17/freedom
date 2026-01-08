from peewee import SqliteDatabase
from back_end.db.db import db

MODELS = [
    
]

def initialize_database():
    db.connect()
    db.create_tables(MODELS, safe=True)
    db.close()