import uuid
from typing import Optional
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin, models
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy
)
from fastapi_users.db import SQLAlchemyUserDatabase
from data.db import User, get_user_db
from config import get_settings

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


settings = get_settings()
token_secret = settings.user_token_secret.get_secret_value()

class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    settings = get_settings()
    token_secret = settings.user_token_secret.get_secret_value()
    reset_password_token_secret=token_secret
    verification_token_secret=token_secret

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(self, user: User, token: str, request: Optional[Request] = None):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(self, user: User, token: str, request: Optional[Request] = None):
        print(f"Verification requested for user {user.id}. Verification token: {token}")


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

def get_jwt_strategy():
    twelve_hours = 43200
    return JWTStrategy(secret=token_secret, lifetime_seconds=twelve_hours)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy
)

fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, auth_backends=[auth_backend])
current_active_user = fastapi_users.current_user(active=True)


async def get_users_dict(session: AsyncSession):
    users_result = await session.execute(select(User))
    users = [row[0] for row in users_result.all()]
    users_dict = {u.id: u.email for u in users}
    return users_dict