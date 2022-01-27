import aiogram.types
from aiogram import types
from aiogram.dispatcher.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from asyncpg import Connection
from load_all import bot, dp, db, _
import logging


class Commands:
    pool: Connection = db
    add_new_user = 'INSERT INTO test(name, nickname, chat_id) VALUES ($1, $2, $3);'
    add_new_user_referral = 'INSERT INTO test(name, nickname, referrals, chat_id) ' \
                            'VALUES ($1, $2, $3, $4);'
    check_name = 'SELECT name FROM test WHERE chat_id = $1;'
    check_nickname = 'SELECT nickname FROM test WHERE chat_id = $1;'
    check_referrals = 'SELECT chat_id FROM test WHERE referrals = $1;'
    check_balance = 'SELECT balance FROM test WHERE chat_id = $1;'
    check_id = 'SELECT id FROM test WHERE chat_id = $1;'
    update_lang = 'UPDATE test SET lang = $1 WHERE chat_id = $2;'
    check_lang = 'SELECT lang FROM test WHERE chat_id = $1'

    async def show_lang(self):
        user = types.User.get_current()
        return await self.pool.fetchval(self.check_lang, user.id)

    async def set_lang(self, slang):
        user = types.User.get_current()
        logging.info('conn to db to set lang - ' + str(slang))
        return await self.pool.fetchval(self.update_lang, slang, user.id)

    async def rgstr(self, referral=None):
        user = types.User.get_current()
        name = user.first_name
        nickname = user.username
        chat_id = user.id

        prove = await self.pool.fetchval(f'SELECT id FROM test WHERE chat_id={chat_id}')
        if prove is None:
            if referral:
                return await self.pool.fetchval(self.add_new_user_referral, name, nickname, referral, chat_id)
            elif not referral:
                return await self.pool.fetchval(self.add_new_user, name, nickname, chat_id)
        else:
            logging.info('you have been added into the database')

    async def id(self):
        id = aiogram.types.User.get_current().id

        return await self.pool.fetchval(self.check_id, id)

    async def name(self):
        chat_id = types.User.get_current().id

        return await self.pool.fetchval(self.check_name, chat_id)

    async def nickname(self):
        chat_id = types.User.get_current().id

        return await self.pool.fetchval(self.check_nickname, chat_id)

    async def referral(self):
        # we get int type (start=43348), so people use bot get_args
        chat_id = str(types.User.get_current().id)

        # bot need to return link on referrals
        # 1. accept arguments
        # 2. create links on these arguments
        # 3. show it
        # 4. if it`s nothing - return space
        refs = await self.pool.fetch(self.check_referrals, chat_id)
        text = ""
        another_text = ""
        for ref in refs:
            logging.info('ref = ' + str(ref['chat_id']))
            link = (await bot.get_chat(ref['chat_id'])).get_mention()
            logging.info(await bot.get_chat(ref['chat_id']))
            text += f'{link}\n'
        return text

    async def balance(self):
        chat_id = types.User.get_current().id

        return await self.pool.fetchval(self.check_balance, chat_id)


base = Commands()


@dp.message_handler(CommandStart())
async def add(message: Message):
    # get record into database and set locale language
    referral = message.get_args()
    logging.info('referrals have been checked')
    await base.rgstr(referral)
    await message.answer(_('your default language - English, to switch it write /lang'))


mark_data = CallbackData('BR', 'lang')


@dp.message_handler(commands='lang')
async def lang(m: Message):
    global mark_data

    mark4 = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='English', callback_data=mark_data.new(lang='en')),
                InlineKeyboardButton(text='Русский', callback_data=mark_data.new(lang='ru'))
            ],
            [
                InlineKeyboardButton(text='Українська', callback_data=mark_data.new(lang='uk'))
            ]
        ]
    )
    await m.answer(_('What language do you prefer?'), reply_markup=mark4)


@dp.callback_query_handler(mark_data.filter(lang='en'))
async def en_lang(call: CallbackQuery, callback_data: dict):
    logging.info(callback_data)
    await base.set_lang(callback_data['lang'])
    await call.message.edit_reply_markup()
    await call.message.edit_text('ok, your language - English')


@dp.callback_query_handler(mark_data.filter(lang='ru'))
async def ru_lang(call: CallbackQuery, callback_data: dict):
    logging.info(callback_data)
    await base.set_lang(callback_data['lang'])
    await call.message.edit_reply_markup()
    await call.message.edit_text('Хорошо, теперь твой язык - Русский')


@dp.callback_query_handler(mark_data.filter(lang='uk'))
async def ru_lang(call: CallbackQuery, callback_data: dict):
    logging.info(callback_data)
    await base.set_lang(callback_data['lang'])
    await call.message.edit_reply_markup()
    await call.message.edit_text('Добре, зараз твоя мова - Українська')


@dp.message_handler(commands="id")
async def id(message: Message):
    user_id = await base.id()
    logging.info('something')
    await message.answer(_('Your id in this database - {0}').format(user_id))


@dp.message_handler(commands=["name"])
async def user_name(message: Message):
    user_name = await base.name()
    await message.answer(_('Your name in telegram - {user_name}').format(user_name=user_name))
    logging.info('{something}.format(something=something)')


@dp.message_handler(commands=["nickname"])
async def user_nickname(message: Message):
    user_nickname = await base.nickname()
    await message.answer(_('Your nickname - {0}').format(user_nickname))


@dp.message_handler(commands='referrals')
async def user_referrals(message: Message):
    user_referrals = await base.referral()
    me = await bot.get_current().get_me()
    user = types.User.get_current().id
    link = f'https://t.me/{me.username}?start={user}'
    text = _('referrals:\n'
             '{0}\n'
             'and your link: {1}').format(user_referrals, link)
    await message.answer(text)


@dp.message_handler(commands=["balance"])
async def user_referrals(message: Message):
    user_balance = await base.balance()

    text = _("Your test-balance in this db = {0}").format(user_balance)
    await message.answer(text)


@dp.message_handler()
async def echo(message: Message):
    logging.info('working')
    await message.answer(f"{message.text}")
