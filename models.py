from sqlalchemy import Column, Integer, String, Float, Date
from database import Base
from enum import Enum
from pydantic import BaseModel
from typing import Optional


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

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
