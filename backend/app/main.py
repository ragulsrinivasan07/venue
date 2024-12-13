from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
import jwt
from datetime import datetime, timedelta
from . import models, services, database
from .config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
from .database import db_engine_session_setup
from fastapi.staticfiles import StaticFiles
from .auth import hash_password, verify_password, create_access_token, verify_token  # Import from auth.py

# Define the User Pydantic model for validation
class User(BaseModel):
    username: str
    password: str

# Initialize the FastAPI app
app = FastAPI()

# Mount the static directory
app.mount("/images", StaticFiles(directory="C:/Users/ragul/HereItIs/Projects/venue/images"), name="images")  

# JWT Authorization configuration
SECRET_KEY = Config.SECRET_KEY
ALGORITHM = Config.ALGORITHM

engine, SessionLocal =  db_engine_session_setup()

def get_db():
    db = SessionLocal()
    try:
        yield db    
    finally:
        db.close()

# Create all tables in the database
Base.metadata.create_all(bind=engine)

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI application! Use /signup or /login endpoints."}

# User Signup endpoint
@app.post("/signup")
async def signup(user: User, db: Session = Depends(get_db)):
    # Check if username already exists
    db_user = services.get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Hash the password before saving it
    hashed_password = hash_password(user.password)
    created_user = services.create_user(db, user.username, hashed_password)
    
    return {"message": "User created successfully"}

# Login endpoint (returns JWT)
@app.post("/login")
async def login(user: User, db: Session = Depends(get_db)):
    db_user = services.get_user_by_username(db, user.username)
    if not db_user:
        raise HTTPException(status_code=400, detail="User not found")
        
    # Check password hash using verify_password
    if not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    # Create JWT token using the auth module
    token = create_access_token(data={"sub": user.username})
    return {"access_token": token}

# Fetch all venues
@app.get("/venues") 
async def get_venues(token: str = Depends(verify_token), db: Session = Depends(get_db)):
    venues = services.get_venues(db)
    return venues

# Fetch specific venue by ID
@app.get("/venue/{venue_id}")
async def get_venue_details(venue_id: int, token: str = Depends(verify_token), db: Session = Depends(get_db)):
    venue = services.get_venue_by_id(db, venue_id)
    if venue:
        return venue
    else:
        raise HTTPException(status_code=404, detail="Venue not found")