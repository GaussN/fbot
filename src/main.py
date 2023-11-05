import asyncio

from loguru import logger

from loader import bot, dp
from handlers import router
from db import engine, Base


async def main():
    # init db
    Base.metadata.create_all(bind=engine)
    logger.info('tables have created')

    # routers
    dp.include_router(router)

    # start
    logger.info('bot working')
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
