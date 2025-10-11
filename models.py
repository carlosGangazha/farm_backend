from sqlalchemy import Column, Integer, String
from database import Base
from enum import Enum
from pydantic import BaseModel
from typing import Optional
from datetime import date as Date, datetime, timezone

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
