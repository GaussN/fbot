from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage, Redis

from config import BOT_TOKEN, REDIS_HOST, REDIS_PORT


bot: Bot = Bot(token=BOT_TOKEN, parse_mode='markdown')
storage: RedisStorage = RedisStorage(Redis())
dp: Dispatcher = Dispatcher(storage=storage)
