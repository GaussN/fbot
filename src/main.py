import asyncio

from loguru import logger

from loader import bot, dp

from handlers.pingpong import router as ping_router
from handlers.info import router as info_router
from handlers.files import router as files_router

from db import engine, Base


async def main():
    # init db
    Base.metadata.create_all(bind=engine)
    logger.info('tables have created')

    # routers
    dp.include_router(ping_router)
    dp.include_router(info_router)
    dp.include_router(files_router)

    # start
    logger.info('bot working')
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
