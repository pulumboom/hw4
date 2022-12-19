from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_inventory_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="<Put On>")
    kb.button(text="<Take Off>")
    kb.button(text="<Drink a Potion>")
    kb.button(text="<Cancel>")
    kb.adjust(1)

    return kb.as_markup(resize_keyboard=True)