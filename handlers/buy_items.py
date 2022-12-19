from aiogram import Router
from aiogram.dispatcher.filters import Text
from aiogram import types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import StatesGroup, State
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from db.models import Persons, Items, Inventory
#from bot import sessiong

from keyboards.buy_items_kb import get_buy_items_kb
from keyboards.choose_item_kb import get_choose_item_kb


class ChooseAction(StatesGroup):
    action_buy = State()
    action_sell = State()


router = Router()


@router.message(Text(text="<Buy&Sell Items>"))
async def buy_items(message: types.Message):
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
        money = user.money

    await message.answer(
        f"<b>Money</b>: {money}\n",
        reply_markup=get_buy_items_kb(),
        parse_mode="html"
    )


@router.message(Text(text="<Buy>"))
async def cmd_buy(message: types.Message, state: FSMContext):
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

        items_to_buy = await session.execute(
            select(Items).where(Items.location_id == user.location_id)
        )
        text = ''
        items = []
        for i, item in enumerate(items_to_buy):
            item = item['Items']
            items.append(item)
            text += f"{i + 1}. {item.item_name}"

        await message.answer(
            f"<b>Money</b>: {user.money}\n"
            f"<b>Items to buy:</b>\n" + text,
            reply_markup=get_choose_item_kb(len(items)),
            parse_mode='html'
        )
        await state.set_state(ChooseAction.action_buy)

        await session.commit()
        await engine.dispose()


@router.message(ChooseAction.action_buy)
async def buy(message: types.Message, state: FSMContext):
    await state.clear()
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

        items_to_buy = await session.execute(
            select(Items).where(Items.location_id == user.location_id)
        )
        items = []
        for item in items_to_buy:
            item = item['Items']
            items.append(item)

        chosen = message.text.rstrip('>').lstrip('<')

        if not chosen.isdigit() or int(chosen) > len(items):
            await message.answer('Choose button!')
            await session.commit()
            await engine.dispose()
            return

        chosen = int(chosen)
        chosen -= 1

        if user.money >= items[chosen].cost:
            user.money -= items[chosen].cost
            relation = Inventory(
                user_id=user.user_id,
                item_id=items[chosen].item_id,
            )
            session.add(relation)
            await message.answer(
                "Successfully bought!"
            )
        else:
            await message.answer(
                "You have no enough money"
            )

        await session.commit()
        await engine.dispose()
        await buy_items(message)


@router.message(Text(text="<Sell>"))
async def cmd_buy(message: types.Message, state: FSMContext):
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
            text += '\n'

        await message.answer(
            f"<b>Money</b>: {user.money}\n"
            "<b>Items to sell:</b>\n" + text,
            reply_markup=get_choose_item_kb(len(inventory_items)),
            parse_mode='html'
        )
        await state.set_state(ChooseAction.action_sell)
        await session.commit()
        await engine.dispose()


@router.message(ChooseAction.action_sell)
async def buy(message: types.Message, state: FSMContext):
    await state.clear()
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

        chosen = message.text.rstrip('>').lstrip('<')

        if not chosen.isdigit() or int(chosen) > len(inventory_items):
            await message.answer('Choose button!')
            await session.commit()
            await engine.dispose()
            return

        chosen = int(chosen)
        chosen -= 1

        user.money += inventory_items[chosen].cost
        relation = await session.execute(
            select(Inventory).where(
                (Inventory.user_id == user.user_id) &
                (Inventory.item_id == inventory_items[chosen].item_id)
            )
        )
        relation = relation.first()['Inventory']
        await session.delete(relation)

        await message.answer(
            "Successfully sold!"
        )

        await session.commit()
        await engine.dispose()
        await buy_items(message)
