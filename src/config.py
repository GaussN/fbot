from os import environ

from loguru import logger


DB_CONNECT_STRING = 'postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}'.format(
    user=environ['POSTGRES_USER'],
    password=environ['POSTGRES_PASSWORD'],
    host=environ['POSTGRES_HOST'],
    port=environ['POSTGRES_PORT'],
    db=environ['POSTGRES_DB'],
)


REDIS_HOST = environ.get('REDIS_HOST', '127.0.0.1')
REDIS_PORT = environ.get('REDIS_PORT', 6379)


BOT_TOKEN = environ['BOT_TOKEN']
BOT_NAME = environ.get('BOT_NAME', 'Gena')

GOOGLE_LOGIN = environ['GOOGLE_LOGIN']
GOOGLE_PASSWORD = environ['GOOGLE_PASSWORD']


logger.trace(f'{DB_CONNECT_STRING=}')
logger.trace(f'{REDIS_HOST=}')
logger.trace(f'{REDIS_PORT}')
logger.trace(f'{BOT_TOKEN=}')
logger.trace(f'{GOOGLE_LOGIN=}')
