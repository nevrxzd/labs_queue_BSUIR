from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def main_menu() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(
        text="Посмотреть расписание",
        callback_data="show_schedule"
        )
    )
    kb.row(InlineKeyboardButton(
        text="Редактировать очередь",
        callback_data="queue"
        )
    )
    kb.row(InlineKeyboardButton(
        text="Написать старосте",
        callback_data="и ты хотел мифические тексты"
        )
    )
    return kb.as_markup()
def start() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(
        text="Приступить",
        callback_data="back_to_main"
        )
    )

    return kb.as_markup()

def queue() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(
        text="Добавить очередь",
        callback_data="add_queue"
        )
    )
    kb.row(InlineKeyboardButton(
        text="Записаться в очередь",
        callback_data="add_to_queue"
        )
    )
    kb.row(InlineKeyboardButton(
        text="Посмотреть существующие",
        callback_data="show_exist_queue"
        )
    )
    kb.row(InlineKeyboardButton(
        text="Назад в главное меню",
        callback_data="back_to_main"
        )
    )
    return kb.as_markup()

def admin() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(
        text="Назад",
        callback_data="back_to_main"
        )
    )
    return kb.as_markup()

def add_queue() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(
        text=""
        )
    )