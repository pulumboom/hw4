import random

from aiogram import Router
from aiogram import types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import StatesGroup, State
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from db.models import Persons, Mobs, Inventory
from handlers.start import cmd_start
from keyboards.fighting_kb import get_initial_fighting_kb, get_fight_kb


class Fighting(StatesGroup):
    fighting_initial_meeting = State()
    fighting_main_stage = State()
    fighting_win = State()


router = Router()


@router.message(Text(text="<Fight>"))
async def fight1(message: types.Message, state: FSMContext):
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

        enemy_hp = await state.get_data()
        enemy_hp = enemy_hp.get('enemy_hp')

        await message.answer(
            f"<b>Your HP:</b> {user.cur_hp}\n"
            f"<b>Enemy's HP:</b> {enemy_hp}",
            parse_mode='html',
            reply_markup=get_fight_kb()
        )
        await state.set_state(Fighting.fighting_main_stage)
        await session.commit()
    await engine.dispose()


@router.message(Text(text="<Mob's info>"))
async def mobs_info(message: types.Message, state: FSMContext):
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

        enemy_id = await state.get_data()
        mobs = await session.execute(
            select(Mobs).where(Mobs.mob_id == enemy_id.get('enemy_id'))
        )
        enemy = mobs.first()["Mobs"]

        info = await state.get_data()

        await message.answer(
            f"<b>Enemy's HP:</b> {info.get('enemy_hp') or enemy.hp}\n"
            f"<b>Enemy's XP:</b> {enemy.hp}\n"
            f"<b>Enemy's attack type:</b> {enemy.attack_type.name}\n"
            f"<b>Enemy's attack:</b> {info.get('enemy_attack') or enemy.attack}\n"
            f"<b>Enemy's armour:</b> {enemy.armour}\n"
            f"<b>Enemy's magic armour:</b> {enemy.magic_armour}\n",
            parse_mode='html'
        )
        await session.commit()
    await engine.dispose()


@router.message(Fighting.fighting_main_stage)
async def fight2(message: types.Message, state: FSMContext):
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

        enemy_hp = await state.get_data()
        enemy_hp = enemy_hp["enemy_hp"]
        if message.text == "<Physical Attack>":
            enemy_hp -= user.attack
        elif message.text == "<Magic Attack>":
            enemy_hp -= user.magic_attack
        await state.update_data(enemy_hp=enemy_hp)

        if enemy_hp <= 0:
            money = await state.get_data()
            user.money += money.get('money')
            await session.commit()
            await state.clear()
            await message.answer("You win!")
            await engine.dispose()
            await cmd_start(message, state)
            return

        enemy_attack = await state.get_data()
        enemy_attack = enemy_attack.get("enemy_attack")
        user.cur_hp -= enemy_attack

        if user.cur_hp <= 0:
            await message.answer("You lose!")
            await state.clear()
            inventory = await session.delete(
                select(Inventory).where(Inventory.user_id == user.user_id)
            )
            await session.delete(user)
            await session.commit()
            await engine.dispose()
            return

        await session.commit()
    await engine.dispose()
    await fight1(message, state)


@router.message(Fighting.fighting_initial_meeting)
async def initial_fighting(message: types.Message, state: FSMContext):
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

        mobs = await session.execute(
            select(Mobs).where(Mobs.req_level <= user.level)
        )
        enemies = []
        for enemy in mobs:
            enemies.append(enemy['Mobs'])

        chosen_enemy = random.choice(enemies)

        await state.update_data(enemy_id=chosen_enemy.mob_id, enemy_hp=chosen_enemy.hp,
                                enemy_attack=chosen_enemy.attack, money=chosen_enemy.xp)

        await message.answer(
            "<b>You're attacked!</b>",
            reply_markup=get_initial_fighting_kb(),
            parse_mode="html"
        )
        await session.commit()
    await engine.dispose()
