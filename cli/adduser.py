import os
import sys

sys.path.insert(0, os.getcwd())

import argparse
import asyncio
from contextlib import asynccontextmanager

from core.security import get_user_manager, get_jwt_strategy
from model import get_user_db, get_session, User

"""
Call:

python .\cli\adduser.py admin admin admin@163.com 1
"""

parser = argparse.ArgumentParser()
parser.add_argument("username", type=str, help="Username of the user to add")
parser.add_argument("password", type=str, help="Password of the user to add")
parser.add_argument("email", type=str, help="Email of the user to add")
parser.add_argument("role", type=str, help="Role of the user to add")


async def adduser(username, password, email, role):
    get_session_ctx = asynccontextmanager(get_session)
    get_user_db_ctx = asynccontextmanager(get_user_db)
    get_user_manager_ctx = asynccontextmanager(get_user_manager)
    jwt_strategy = get_jwt_strategy()
    async with get_session_ctx() as session:
        async with get_user_db_ctx(session) as user_db:
            session = user_db.session
            async with get_user_manager_ctx(user_db) as user_manager:
                password_helper = user_manager.password_helper
                hashed_password = password_helper.hash(password)
                new = User(
                    username=username,
                    hashed_password=hashed_password,
                    email=email,
                    user_type=role
                )
                session.add(new)
                await session.commit()


async def main():
    args = parser.parse_args()
    await adduser(args.username, args.password, args.email, args.role)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
