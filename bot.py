import asyncio
import logging

from aiogram import Bot, Dispatcher
from config_reader import config
from sqlalchemy.ext.asyncio import create_async_engine

from handlers import start, change_location, more_info, inventory, buy_items, fighting

from db.models import Base

engine = None


async def main():
    # Bot
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=config.bot_token.get_secret_value())
    dp = Dispatcher()

    # DataBase
    global engine
    engine = create_async_engine('sqlite+aiosqlite:///game.db', echo=True, encoding='utf-8')
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Routers
    dp.include_router(start.router)
    dp.include_router(change_location.router)
    dp.include_router(more_info.router)
    dp.include_router(inventory.router)
    dp.include_router(buy_items.router)
    dp.include_router(fighting.router)

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
