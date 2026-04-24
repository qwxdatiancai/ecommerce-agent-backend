
from fastapi import FastAPI

from model.user import User
from schemas.user import *
from core.security import auth_backend, current_active_user, fastapi_users


def register_user_routers(app: FastAPI):
    """
    register user routers
    :param app:
    :return:
    """
    app.include_router(
        fastapi_users.get_auth_router(auth_backend), prefix="/v1/user", tags=["user"]
    )
    app.include_router(
        fastapi_users.get_register_router(UserRead, UserCreate),
        prefix="/v1/user",
        tags=["user"],
    )
    app.include_router(
        fastapi_users.get_reset_password_router(),
        prefix="/v1/user",
        tags=["user"],
    )
    app.include_router(
        fastapi_users.get_verify_router(UserRead),
        prefix="/v1/user",
        tags=["user"],
    )
    app.include_router(
        fastapi_users.get_users_router(UserRead, UserUpdate),
        prefix="/v1/user",
        tags=["user"],
    )
