# src/models.py
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from enum import Enum
from fastapi_users import schemas
from uuid import UUID
    
class PostCreate(BaseModel):
    title: str
    content: str

class PostResponse(BaseModel):
    id: UUID
    caption: str
    file_type: str
    file_name: str | None = None
    
    class Config:
        from_attributes = True # Allows Pydantic to read data from SQLAlchemy objects

class UserRead(schemas.BaseUser[UUID]):
    pass

class UserCreate(schemas.BaseUserCreate):
    pass

class UserUpdate(schemas.BaseUserUpdate):
    pass