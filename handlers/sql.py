import asyncpg
from config import user, host, sword


async def create():
    return await asyncpg.create_pool(
        user=user,
        password=sword,
        host=host
    )
