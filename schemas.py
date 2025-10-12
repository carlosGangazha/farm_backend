from pydantic import BaseModel, constr
from datetime import date, datetime  # Import specific classes
from typing import Optional, List

class UserCreate(BaseModel):
    username: str
    email: str
    password: constr(min_length=6, max_length=72) # type: ignore

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class CropBase(BaseModel):
    name: str
    area: float
    planting_date: date
    harvest_date: date

class CropCreate(CropBase):
    pass

class CropResponse(CropBase):
    id: int

    class Config:
        orm_mode = True

class LivestockCreate(BaseModel):
    type: str
    breed: str
    count: int
    notes: Optional[str] = None

class LivestockUpdate(BaseModel):
    type: Optional[str] = None
    breed: Optional[str] = None
    count: Optional[int] = None
    notes: Optional[str] = None

class LivestockResponse(BaseModel):
    id: int
    type: str
    breed: str
    count: int
    notes: Optional[str] = None

# GIS schemas - FIXED
class Coordinate(BaseModel):
    lat: float
    lng: float

class FieldCreate(BaseModel):
    name: str
    coordinates: List[Coordinate]  # Use List from typing
    area: float
    ndvi: Optional[float] = None

class FieldResponse(BaseModel):
    id: int
    name: str
    coordinates: List[Coordinate]
    center: Coordinate
    area: float
    ndvi: Optional[float] = None
    last_updated: datetime
    
    class Config:
        from_attributes = True