from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey,DateTime
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from database import Base
from enum import Enum
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Field(Base):
    __tablename__ = "fields"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    area = Column(Float)
    ndvi = Column(Float, nullable=True)
    geometry = Column(Geometry('POLYGON', srid=4326))
    center_lat = Column(Float)
    center_lng = Column(Float)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Add 
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    user = relationship("User", back_populates="fields")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    fields = relationship("Field", back_populates="user")

class Crop(Base):
    __tablename__ = "crops"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    area = Column(Float, nullable=False)
    planting_date = Column(Date, nullable=False)
    harvest_date = Column(Date, nullable=False)

class Livestock(Base):
    __tablename__ = "livestock"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(100), nullable=False)
    breed = Column(String(100), nullable=False)
    count = Column(Integer, nullable=False)
    notes = Column(String(500), nullable=True)
