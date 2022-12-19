from aiogram import Router
from aiogram.dispatcher.filters import Text
from aiogram import types
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from db.models import Persons
from keyboards.more_info_kb import get_more_info_kb

router = Router()


@router.message(Text(text="<More Info>"))
async def more_info(message: types.Message):
    engine = create_async_engine('sqlite+aiosqlite:///game.db', echo=True, encoding='utf-8')
    async_session = sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        user = await session.execute(
            select(Persons).where(Persons.user_id == str(message.from_user.id))
        )
        user = user.first()['Persons']
        if not user:
            await message.answer("Run /start first.")
            await session.commit()
            await engine.dispose()
            return

        nickname = user.nickname
        level = user.level
        cur_hp = user.cur_hp
        hp = user.hp
        cur_xp = user.xp
        armour = user.armour
        magic_armour = user.magic_armour
        weapon = user.weapon
        helmet = user.helmet
        chest_plate = user.chest_plate
        pants = user.pants
        boots = user.boots
        await session.commit()
    await message.answer(
        f"<b>Nickname</b>: {nickname}\n"
        f"<b>Level</b>: {level}\n"
        f"<b>Current HP</b>: {cur_hp}/{hp}\n"
        f"<b>Current XP</b>: {cur_xp}/100\n"
        f"<b>Armour</b>: {armour}\n"
        f"<b>Magic Armour</b>: {magic_armour}\n"
        f"<b>Weapon</b>: {weapon}\n"
        f"<b>Helmet</b>: {helmet}\n"
        f"<b>Chest Plate</b>: {chest_plate}\n"
        f"<b>Pants</b>: {pants}\n"
        f"<b>Boots</b>: {boots}\n",
        reply_markup=get_more_info_kb(),
        parse_mode="html"
    )
    await engine.dispose()
