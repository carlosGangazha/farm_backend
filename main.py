from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import Base, engine, get_db
from models import User, Crop, Livestock
from schemas import UserCreate, UserLogin, Token, CropResponse, CropCreate, LivestockResponse, LivestockCreate
from auth import hash_password, verify_password, create_access_token

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Farm Management")

# CORS Configuration - Allow all Vercel deployments
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://ruth-project-64ut.vercel.app",
    # Temporarily allow all origins to test (REMOVE IN PRODUCTION)
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,  # MUST be False when using "*"
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Content-Type", "Authorization", "Accept", "Origin"],
    expose_headers=["*"],
    max_age=3600,
)

# Health check endpoint
@app.get("/")
def read_root():
    return {"status": "healthy", "message": "Farm Management API"}

# Authentication endpoints
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

# Crop endpoints
@app.post("/crops", response_model=CropResponse, status_code=status.HTTP_201_CREATED)
def create_crop(crop: CropCreate, db: Session = Depends(get_db)):
    new_crop = Crop(
        name=crop.name,
        area=crop.area,
        planting_date=crop.planting_date,
        harvest_date=crop.harvest_date
    )
    db.add(new_crop)
    db.commit()
    db.refresh(new_crop)
    return new_crop

@app.get("/crops", response_model=list[CropResponse])
def get_crops(db: Session = Depends(get_db)):
    return db.query(Crop).all()

@app.get("/crops/{crop_id}", response_model=CropResponse)
def get_crop(crop_id: int, db: Session = Depends(get_db)):
    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")
    return crop

@app.put("/crops/{crop_id}", response_model=CropResponse)
def update_crop(crop_id: int, crop_data: CropCreate, db: Session = Depends(get_db)):
    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")

    crop.name = crop_data.name
    crop.area = crop_data.area
    crop.planting_date = crop_data.planting_date
    crop.harvest_date = crop_data.harvest_date
    db.commit()
    db.refresh(crop)
    return crop

@app.delete("/crops/{crop_id}")
def delete_crop(crop_id: int, db: Session = Depends(get_db)):
    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")

    db.delete(crop)
    db.commit()
    return {"message": "Crop deleted successfully"}

# Livestock endpoints (following exact same pattern as crops)
@app.post("/livestock", response_model=LivestockResponse, status_code=status.HTTP_201_CREATED)
def create_livestock(livestock: LivestockCreate, db: Session = Depends(get_db)):
    new_livestock = Livestock(
        type=livestock.type,
        breed=livestock.breed,
        count=livestock.count,
        notes=livestock.notes
    )
    db.add(new_livestock)
    db.commit()
    db.refresh(new_livestock)
    return new_livestock

@app.get("/livestock", response_model=list[LivestockResponse])
def get_livestock(db: Session = Depends(get_db)):
    return db.query(Livestock).all()

@app.get("/livestock/{livestock_id}", response_model=LivestockResponse)
def get_livestock(livestock_id: int, db: Session = Depends(get_db)):
    livestock = db.query(Livestock).filter(Livestock.id == livestock_id).first()
    if not livestock:
        raise HTTPException(status_code=404, detail="Livestock not found")
    return livestock

@app.put("/livestock/{livestock_id}", response_model=LivestockResponse)
def update_livestock(livestock_id: int, livestock_data: LivestockCreate, db: Session = Depends(get_db)):
    livestock = db.query(Livestock).filter(Livestock.id == livestock_id).first()
    if not livestock:
        raise HTTPException(status_code=404, detail="Livestock not found")

    livestock.type = livestock_data.type
    livestock.breed = livestock_data.breed
    livestock.count = livestock_data.count
    livestock.notes = livestock_data.notes
    db.commit()
    db.refresh(livestock)
    return livestock

@app.delete("/livestock/{livestock_id}")
def delete_livestock(livestock_id: int, db: Session = Depends(get_db)):
    livestock = db.query(Livestock).filter(Livestock.id == livestock_id).first()
    if not livestock:
        raise HTTPException(status_code=404, detail="Livestock not found")

    db.delete(livestock)
    db.commit()
    return {"message": "Livestock deleted successfully"}