from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

import typing


def get_change_location_kb(locations: int) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="<Map>")
    for i in range(1, locations + 1):
        kb.button(text=f"<{i}>")
    kb.button(text="<Cancel>")
    kb.adjust(1)

    return kb.as_markup(resize_keyboard=True)
