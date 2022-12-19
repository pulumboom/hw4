from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

import typing


def get_choose_item_kb(locations: int) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    for i in range(1, locations + 1):
        kb.button(text=f"<{i}>")
    kb.button(text="<Cancel>")
    kb.adjust(1)

    return kb.as_markup(resize_keyboard=True)
