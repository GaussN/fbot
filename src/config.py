from os import environ

from loguru import logger


DB_CONNECT_STRING = 'postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}'.format(
    user=environ['POSTGRES_USER'],
    password=environ['POSTGRES_PASSWORD'],
    host=environ['POSTGRES_HOST'],
    port=environ['POSTGRES_PORT'],
    db=environ['POSTGRES_DB'],
)

REDIS_CONNECT_STRING = NotImplemented

BOT_TOKEN = environ['BOT_TOKEN']


logger.debug(f'{DB_CONNECT_STRING=}')
logger.debug(f'{REDIS_CONNECT_STRING=}')
logger.debug(f'{BOT_TOKEN=}')
