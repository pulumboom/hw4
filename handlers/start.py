from aiogram import Router
from aiogram import types
from aiogram.dispatcher.filters import Command, Text
from aiogram.dispatcher.fsm.context import FSMContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from aiogram.dispatcher.fsm.state import StatesGroup, State

from db.models import Persons, Locations
from keyboards.start_kb import get_start_kb


router = Router()


@router.message(Command(commands=["start"]))
@router.message(Text(text="<Cancel>"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()

    engine = create_async_engine('sqlite+aiosqlite:///game.db', echo=True, encoding='utf-8')
    async_session = sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        user = await session.execute(
            select(Persons).where(Persons.user_id == str(message.from_user.id))
        )
        user = user.first()
        if user:
            user = user['Persons']
            nickname = user.nickname
            location = await session.execute(
                select(Locations).where(Locations.location_id == user.location_id)
            )
            location = location.first()['Locations']
            cur_hp = user.cur_hp
            hp = user.hp
            cur_xp = user.xp
            money = user.money
        else:
            nickname = message.from_user.username
            location = await session.execute(
                select(Locations).where(Locations.location_name == 'Hometown')
            )
            location = location.first()['Locations']
            cur_hp = 100
            hp = 100
            cur_xp = 0
            money = 100
            user = Persons(
                user_id=message.from_user.id,
                nickname=message.from_user.username,
                level=1,
                hp=100,
                cur_hp=100,
                money=100,
                attack=1,
                magic_attack=1,
                xp=0,
                armour=0,
                magic_armour=0,
                location_id=location.location_id
            )
            session.add(user)
        await session.commit()

    await message.answer(
        f"<b>Nickname:</b> {nickname}\n"
        f"<b>Location:</b> {location.location_name}\n"
        f"<b>Current HP:</b> {cur_hp}/{hp}\n"
        f"<b>Current XP:</b> {cur_xp}/100\n"
        f"<b>Money:</b> {money}\n",
        reply_markup=get_start_kb(),
        parse_mode="html"
    )
    await engine.dispose()
