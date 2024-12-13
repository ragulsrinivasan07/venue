from sqlalchemy.orm import Session
from .models import User, Venue  # Import User and Venue from models
import hashlib
# from .auth import hash_password
from . import models

# Function to create a new user
def create_user(db, username: str, password: str):
    # hashed_password = hash_password(password)
    db_user = models.User(username=username, password=password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Function to get a user by username
def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()  # Use User directly

# Function to get all venues
def get_venues(db: Session):
    return db.query(Venue).all()

# Function to get a specific venue
def get_venue_by_id(db: Session, venue_id: int):
    return db.query(Venue).filter(Venue.id == venue_id).first()