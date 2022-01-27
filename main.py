from aiogram.utils import executor

from handlers.handlers import dp
from load_all import bot

from config import id


async def on_startup(dp):
    await bot.send_message(id, "hi, i`m ready)")


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)
