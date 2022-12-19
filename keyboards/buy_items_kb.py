from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_buy_items_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="<Buy>")
    kb.button(text="<Sell>")
    kb.button(text="<Cancel>")
    kb.adjust(1)

    return kb.as_markup(resize_keyboard=True)
