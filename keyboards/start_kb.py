from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_start_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="<Change Location>")
    kb.button(text="<More Info>")
    kb.button(text="<Inventory>")
    kb.button(text="<Buy&Sell Items>")
    kb.adjust(1)

    return kb.as_markup(resize_keyboard=True)
