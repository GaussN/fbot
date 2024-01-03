import logging
import asyncio

from loader import bot, dp
from handlers import router
from db import engine, Base

from log import setup_logging


async def main():
    setup_logging()
    logger = logging.getLogger('app')

    # Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # routers
    dp.include_router(router)

    # start
    logger.info('bot start working')
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
