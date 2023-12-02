import asyncio
import sys

from loguru import logger

logger.remove(0)
logger.add(sys.stdout, level=0)

from loader import bot, dp
from handlers import router
from db import engine, Base


async def main():
    # init db
    # Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    logger.info('tables have been created')

    # routers
    dp.include_router(router)

    # start
    logger.info('bot working')
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
