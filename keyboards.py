from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def keyboard_sofa(back_id, next_id):
    url = InlineKeyboardButton("Купить этот диван", url="https://example.com/")
    button_back = InlineKeyboardButton("Назад", callback_data=str(back_id))
    button_next = InlineKeyboardButton("Вперёд", callback_data=str(next_id))
    keyboard = InlineKeyboardMarkup()
    keyboard.insert(url)
    keyboard.row(button_back, button_next)
    return keyboard
