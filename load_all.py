import asyncio
import logging
from typing import Callable, Any

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import *
from handlers.sql import create
from middlewares.localize import I18nMiddle

logging.basicConfig(format='[%(filename)s] : [LINE-%(lineno)s] : [%(levelname)s] : [%(funcName)s()] : %('
                           'message)s',
                    level='INFO')

loop = asyncio.get_event_loop()

storage = MemoryStorage()

bot = Bot(tok, parse_mode='HTML')
dp = Dispatcher(bot, storage=storage, loop=loop)
db = dp.loop.run_until_complete(create())

i18n = I18nMiddle(I18N_DOMAIN, LOCALES_DIR)

dp.middleware.setup(i18n)

_: Callable[[Any, Any, int, Any], str] = i18n.gettext
