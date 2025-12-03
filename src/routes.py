from fastapi import FastAPI, HTTPException
from data.users import users_data
from typing import Optional
import logging
import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = FastAPI().router

@router.get("/hello-world")
def hello_world():
    return {"message": "Hello World"}

@router.get("/users")
def get_users(limit: Optional[int] = None):
    logger.info("/api/users was called successfully: " + str(datetime.datetime.now()))

    if limit:
        return users_data[:limit]
    return users_data

@router.get("/users/{user_id}")
def get_user(user_id: int):
    logger.info(f"/api/users/{user_id} was called successfully: " + str(datetime.datetime.now()))
    user = next((user for user in users_data if user['id'] == user_id), None)
    if user:
        return user
    raise HTTPException(status_code=404, detail="User not found")