from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import Base, engine, get_db
from models import User
from schemas import UserCreate, UserLogin, Token
from auth import hash_password, verify_password, create_access_token
import re

app = FastAPI(title="Farm Management")

# CORS Configuration
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://ruth-project-64ut.vercel.app",  # Your production Vercel URL
]

# Custom CORS handler to allow all Vercel preview deployments
def is_allowed_origin(origin: str) -> bool:
    """Check if origin is in allowed list or is a Vercel preview deployment"""
    if origin in origins:
        return True
    vercel_pattern = r"https://ruth-project-[a-z0-9]+-carlosgangazhas-projects\.vercel\.app"
    if re.match(vercel_pattern, origin):
        return True
    return False

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins + ["https://ruth-project-64ut.vercel.app"],
    allow_origin_regex=r"https://ruth-project-[a-z0-9]+-carlosgangazhas-projects\.vercel\.app",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.get("/")
def read_root():
    return {"status": "healthy", "message": "Farm Management API"}

@app.post("/signup", response_model=Token)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    # Check existing user
    db_user = (
        db.query(User)
        .filter((User.email == user.email) | (User.username == user.username))
        .first()
    )
    if db_user:
        raise HTTPException(status_code=400, detail="Email or username already registered")

    hashed_pw = hash_password(user.password)
    new_user = User(username=user.username, email=user.email, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    token = create_access_token({"sub": new_user.email}, new_user.username)
    return {"access_token": token, "token_type": "bearer"}

@app.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": db_user.email}, db_user.username)
    return {"access_token": token, "token_type": "bearer"}