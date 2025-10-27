from database.db import engine, Base
from database.tables import Game, User

def create_tables():
    """Create database tables based on the defined models."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created.")
    # if the tables already exist, they will not be recreated or modified