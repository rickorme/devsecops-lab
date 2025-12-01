# src/models.py
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from enum import Enum

class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"

class User(BaseModel):
    id: int
    name: str
    email: EmailStr
    age: Optional[int] = None
    role: Role = Role.USER

    @field_validator("id")
    def id_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("ID must be a positive integer")
        return v