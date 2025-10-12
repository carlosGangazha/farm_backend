from pydantic import BaseModel, constr
from datetime import date
from typing import Optional

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
