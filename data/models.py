# src/models.py
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from enum import Enum
from fastapi_users import schemas
import uuid
    
class PostCreate(BaseModel):
    title: str
    content: str

class PostResponse(BaseModel):
    title: str
    content: str

class UserRead(schemas.BaseUser[uuid.UUID]):
    pass

class UserCreate(schemas.BaseUserCreate):
    pass

class UserUpdate(schemas.BaseUserUpdate):
    pass