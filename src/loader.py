from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage, Redis

from config import BOT_TOKEN, REDIS_HOST, REDIS_PORT
from db import Session


bot: Bot = Bot(token=BOT_TOKEN, parse_mode='markdown')
storage: RedisStorage = RedisStorage(Redis(host=REDIS_HOST, port=REDIS_PORT))
dp: Dispatcher = Dispatcher(storage=storage, db_session=Session)
