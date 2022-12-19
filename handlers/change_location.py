import asyncio

from aiogram import Router
from aiogram.dispatcher.filters import Text
from aiogram import types
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.dispatcher.fsm.context import FSMContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from db.models import Persons, Routes, Locations
from handlers.fighting import Fighting, initial_fighting

from keyboards.change_location_kb import get_change_location_kb
from handlers.start import cmd_start


class ChooseLocation(StatesGroup):
    choosing_available_location = State()


router = Router()


@router.message(Text(text="<Change Location>"))
async def change_location(message: types.Message, state: FSMContext):
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
        available_locations = await session.execute(
            select(Routes).where(Routes.from_location == str(user.location_id))
        )
        location_ids = []
        for location in available_locations:
            location_ids.append(location['Routes'].to_location)

        to_locations = []
        text_to_write = ''
        for i, location_id in enumerate(location_ids, start=1):
            location = await session.execute(
                select(Locations).where(Locations.location_id == str(location_id))
            )
            location = location.first()['Locations']
            to_locations.append(location)
            text_to_write += f"*\<{i}\>* {location.location_name} \({location.location_type.name}\)\n"
        await session.commit()

    await message.answer(
        f"*Available Locations:* \n" + text_to_write,
        reply_markup=get_change_location_kb(len(to_locations)),
        parse_mode="MarkdownV2"
    )
    await state.set_state(ChooseLocation.choosing_available_location)
    await engine.dispose()


@router.message(ChooseLocation.choosing_available_location)
async def location_choose(message: types.Message, state: FSMContext):
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

        available_locations = await session.execute(
            select(Routes).where(Routes.from_location == str(user.location_id))
        )
        location_ids = []
        for location in available_locations:
            location_ids.append(location['Routes'].to_location)

        to_locations = []
        for i, location_id in enumerate(location_ids, start=1):
            location = await session.execute(
                select(Locations).where(Locations.location_id == str(location_id))
            )
            location = location.first()['Locations']
            to_locations.append(location)

        chosen = message.text.rstrip('>').lstrip('<')

        if chosen == "Map":
            await cmd_map(message)
        elif not chosen.isdigit():
            await message.answer("Choose button!")
            await session.commit()
            await engine.dispose()
            return
        else:
            chosen = int(chosen)
            chosen -= 1
            if chosen > len(to_locations):
                await message.answer("Choose button!")
                await session.commit()
                await engine.dispose()
                return

        route = await session.execute(
            select(Routes).where(
                (Routes.from_location == str(user.location_id)) &
                (Routes.to_location == str(to_locations[chosen].location_id))
            )
        )
        route = route.first()["Routes"]

        current_location = await session.execute(
            select(Locations).where(
                (Locations.location_id == str(user.location_id))
            )
        )
        current_location = current_location.first()["Locations"]

        send_msg = await message.answer(
            "<b>You're on the path:</b>\n"
            f"<b>From:</b> {current_location.location_name}\n"
            f"<b>To:</b> {to_locations[chosen].location_name}\n"
            "<b>Progress:</b> ▯▯▯▯▯▯▯▯▯▯ 0%",
            parse_mode="html",
            reply_markup=None
        )
        progress = 0

        step = 100 // route.time

        for i in range(route.time):
            progress += step

            progress_bar = ['▮'] * (progress // 10) + ['▯'] * (10 - (progress // 10))

            await asyncio.sleep(1)
            send_msg = await send_msg.edit_text(
                "<b>You're on the path:</b>\n"
                f"<b>From:</b> {current_location.location_name}\n"
                f"<b>To:</b> {to_locations[chosen].location_name}\n"
                f"<b>Progress:</b> {''.join(progress_bar)} {progress}%",
                parse_mode="html"
            )

        await send_msg.edit_text(
            "Successfully arrived ✔"
        )

        user.location_id = to_locations[chosen].location_id

        await state.clear()

        if to_locations[chosen].location_type.name == 'City':
            user.cur_hp = user.hp
            await session.commit()
            await engine.dispose()
            await cmd_start(message, state)
        elif to_locations[chosen].location_type.name == 'Underground':
            await state.set_state(Fighting.fighting_main_stage)
            await session.commit()
            await engine.dispose()
            await initial_fighting(message, state)


@router.message(Text(text="<Map>"))
async def cmd_map(message: types.Message):
    await message.answer_photo(photo='https://disk.yandex.ru/i/4CxNdlcLYCNb7Q')


