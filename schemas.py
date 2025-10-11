from pydantic import BaseModel, constr
from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


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