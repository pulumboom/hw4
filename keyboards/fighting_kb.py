from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_initial_fighting_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="<Mob's info>")
    kb.button(text="<Use potion>")
    kb.button(text="<Fight>")
    kb.adjust(1)

    return kb.as_markup(resize_keyboard=True)


def get_fight_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text='<Physical Attack>')
    kb.button(text='<Magic Attack>')
    kb.adjust(1)

    return kb.as_markup(resize_keyboard=True)