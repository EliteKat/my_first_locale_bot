from typing import Tuple, Any, Optional
from aiogram import types
from aiogram.contrib.middlewares.i18n import I18nMiddleware


async def get_lang():
    user = types.User.get_current()
    from load_all import db
    return await db.fetchval('SELECT lang FROM test WHERE chat_id = $1', user.id)


class I18nMiddle(I18nMiddleware):
    async def get_user_locale(self, action: str, args: Tuple[Any]) -> Optional[str]:
        user = types.User.get_current()
        return await get_lang() or user.locale
