
import uuid

from fastapi_users import schemas


class UserRead(schemas.BaseUser[uuid.UUID]):

    username: str
    user_type: int


class UserCreate(schemas.BaseUserCreate):

    username: str
    user_type: int


class UserUpdate(schemas.BaseUserUpdate):

    username: str
