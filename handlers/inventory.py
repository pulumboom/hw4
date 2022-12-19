from aiogram import Router
from aiogram.dispatcher.filters import Text
from aiogram import types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import StatesGroup, State
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from db.models import Persons, Inventory, Items
from keyboards.choose_item_kb import get_choose_item_kb
from keyboards.inventory_kb import get_inventory_kb


class ChooseAction(StatesGroup):
    action_put_on = State()
    action_take_off = State()
    action_drink_portion = State()


router = Router()


@router.message(Text(text="<Inventory>"))
async def cmd_inventory(message: types.Message):
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

        user_items = await session.execute(
            select(Inventory).where(Inventory.user_id == user.user_id)
        )
        inventory_item_ids = []
        worn_item_ids = []
        for item in user_items:
            item = item['Inventory']
            inventory_item_ids.append(item.item_id)
            if item.status == 1:
                worn_item_ids.append(item.item_id)

        inventory_items = []
        for item_id in inventory_item_ids:
            item = await session.execute(
                select(Items).where(Items.item_id == item_id)
            )
            item = item.first()['Items']
            inventory_items.append(item)

        text = ''
        for i, item in enumerate(inventory_items):
            text += f"{i + 1}. {item.item_name}"
            if item.item_id in worn_item_ids:
                text += " (worn)"
            text += '\n'
        await session.commit()

    await message.answer(
        f"<b>Inventory:</b> \n" + text,
        reply_markup=get_inventory_kb(),
        parse_mode="html"
    )
    await engine.dispose()


@router.message(Text(text='<Put On>'))
async def cmd_put_on(message: types.Message, state: FSMContext):
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

        user_items = await session.execute(
            select(Inventory).where(Inventory.user_id == user.user_id)
        )
        inventory_item_ids = []
        for item in user_items:
            item = item['Inventory']
            if item.status == 0:
                inventory_item_ids.append(item.item_id)

        inventory_items = []
        for item_id in inventory_item_ids:
            item = await session.execute(
                select(Items).where(Items.item_id == item_id)
            )
            item = item.first()['Items']
            inventory_items.append(item)

        await session.commit()

    text = ''
    for i, item in enumerate(inventory_items):
        text += f"{i + 1}. {item.item_name}"
        text += '\n'

    await message.answer(
        "<b>Available to put on:</b>\n" + text,
        parse_mode='html',
        reply_markup=get_choose_item_kb(len(inventory_items))
    )
    await state.set_state(ChooseAction.action_put_on)
    await engine.dispose()


@router.message(ChooseAction.action_put_on)
async def put_on(message: types.Message, state: FSMContext):
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

        user_items = await session.execute(
            select(Inventory).where(Inventory.user_id == user.user_id)
        )
        inventory_item_ids = []
        for item in user_items:
            item = item['Inventory']
            if item.status == 0:
                inventory_item_ids.append(item.item_id)

        inventory_items = []
        for item_id in inventory_item_ids:
            item = await session.execute(
                select(Items).where(Items.item_id == item_id)
            )
            item = item.first()['Items']
            inventory_items.append(item)

        chosen = message.text.rstrip('>').lstrip('<')

        if not chosen.isdigit() or int(chosen) > len(inventory_items):
            await message.answer('Choose button!')
            await session.commit()
            await engine.dispose()
            return

        chosen = int(chosen)
        chosen -= 1

        user.attack += inventory_items[chosen].attack
        user.magic_attack += inventory_items[chosen].magic_attack
        user.magic_attack += inventory_items[chosen].magic_attack
        user.armour += inventory_items[chosen].armour
        user.magic_armour += inventory_items[chosen].magic_armour

        if inventory_items[chosen].item_type.name == "Weapon":
            user.weapon = inventory_items[chosen].item_name
        elif inventory_items[chosen].item_type.name == "ChestPlate":
            user.chest_plate = inventory_items[chosen].item_name
        elif inventory_items[chosen].item_type.name == "Helmet":
            user.helmet = inventory_items[chosen].item_name
        elif inventory_items[chosen].item_type.name == "Boots":
            user.boots = inventory_items[chosen].item_name
        elif inventory_items[chosen].item_type.name == "Pants":
            user.pants = inventory_items[chosen].item_name
        elif inventory_items[chosen].item_type.name == "Bracers":
            user.bracers = inventory_items[chosen].item_name

        relation = await session.execute(
            select(Inventory).where(
                (Inventory.user_id == user.user_id) &
                (Inventory.item_id == inventory_items[chosen].item_id)
            )
        )
        relation = relation.first()['Inventory']
        relation.status = 1

        await message.answer(
            "Successfully put on!"
        )

        await session.commit()
        await state.clear()
    await engine.dispose()
    await cmd_inventory(message)


@router.message(Text(text='<Take Off>'))
async def cmd_put_on(message: types.Message, state: FSMContext):
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

        user_items = await session.execute(
            select(Inventory).where(Inventory.user_id == user.user_id)
        )
        inventory_item_ids = []
        for item in user_items:
            item = item['Inventory']
            if item.status == 1:
                inventory_item_ids.append(item.item_id)

        inventory_items = []
        for item_id in inventory_item_ids:
            item = await session.execute(
                select(Items).where(Items.item_id == item_id)
            )
            item = item.first()['Items']
            inventory_items.append(item)

        await session.commit()

    text = ''
    for i, item in enumerate(inventory_items):
        text += f"{i + 1}. {item.item_name} (worn)"
        text += '\n'

    await message.answer(
        "<b>Available to take off:</b>\n" + text,
        parse_mode='html',
        reply_markup=get_choose_item_kb(len(inventory_items))
    )
    await state.set_state(ChooseAction.action_take_off)
    s = await state.get_state()
    await engine.dispose()


@router.message(ChooseAction.action_take_off)
async def put_on(message: types.Message, state: FSMContext):
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

        user_items = await session.execute(
            select(Inventory).where(Inventory.user_id == user.user_id)
        )
        inventory_item_ids = []
        for item in user_items:
            item = item['Inventory']
            if item.status == 1:
                inventory_item_ids.append(item.item_id)

        inventory_items = []
        for item_id in inventory_item_ids:
            item = await session.execute(
                select(Items).where(Items.item_id == item_id)
            )
            item = item.first()['Items']
            inventory_items.append(item)

        chosen = message.text.rstrip('>').lstrip('<')

        if not chosen.isdigit() or int(chosen) > len(inventory_items):
            await message.answer('Choose button!')
            await session.commit()
            await engine.dispose()
            return

        chosen = int(chosen)
        chosen -= 1

        user.attack -= inventory_items[chosen].attack
        user.magic_attack -= inventory_items[chosen].magic_attack
        user.magic_attack -= inventory_items[chosen].magic_attack
        user.armour -= inventory_items[chosen].armour
        user.magic_armour -= inventory_items[chosen].magic_armour

        if inventory_items[chosen].item_type.name == "Weapon":
            user.weapon = 'None'
        elif inventory_items[chosen].item_type.name == "ChestPlate":
            user.chest_plate = 'None'
        elif inventory_items[chosen].item_type.name == "Helmet":
            user.helmet = 'None'
        elif inventory_items[chosen].item_type.name == "Boots":
            user.boots = 'None'
        elif inventory_items[chosen].item_type.name == "Pants":
            user.pants = 'None'
        elif inventory_items[chosen].item_type.name == "Bracers":
            user.bracers = 'None'

        relation = await session.execute(
            select(Inventory).where(
                (Inventory.user_id == user.user_id) &
                (Inventory.item_id == inventory_items[chosen].item_id)
            )
        )
        relation = relation.first()['Inventory']
        relation.status = 0

        await message.answer(
            "Successfully took off!"
        )

        await session.commit()
        await state.clear()
    await engine.dispose()
    await cmd_inventory(message)
