from aiogram import Router

from .info import router as info_router
from .pingpong import router as pong_router
from .files import router as fiels_router
from .auth import router as auth_router

router = Router()


router.include_routers(info_router, pong_router, auth_router, fiels_router)
