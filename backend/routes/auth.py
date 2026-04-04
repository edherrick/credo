import os
import uuid

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from database import async_session_maker, get_db
from models.user import User, UserProfile

SECRET = os.environ.get("SECRET_KEY", "changeme")


async def get_user_db(session: AsyncSession = Depends(get_db)):
    yield SQLAlchemyUserDatabase(session, User)


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Request | None = None):
        # Auto-create user_profile on registration.
        # Username was validated on the UserCreate schema; fall back to email prefix if absent.
        username = getattr(user, "_register_username", user.email.split("@")[0])
        async with async_session_maker() as session:
            profile = UserProfile(user_id=user.id, username=username)
            session.add(profile)
            await session.commit()

    async def create(self, user_create, safe: bool = False, request: Request | None = None):
        # Stash username so on_after_register can use it
        user = await super().create(user_create, safe=safe, request=request)
        user._register_username = getattr(user_create, "username", user.email.split("@")[0])
        return user


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)


bearer_transport = BearerTransport(tokenUrl="/api/v1/auth/login")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600 * 24 * 7)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])

current_active_user = fastapi_users.current_user(active=True)
