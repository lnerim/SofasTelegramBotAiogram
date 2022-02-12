from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def keyboard_sofa(back_id, next_id, price):
    """ Клавиатура для выбора дивана из каталога """
    url = InlineKeyboardButton(f"Купить за {price} руб", url="https://example.com/")
    line = []
    if back_id is not None:
        line.append(InlineKeyboardButton("⬅ Назад", callback_data=str(back_id)))
    if next_id is not None:
        line.append(InlineKeyboardButton("Вперёд ➡", callback_data=str(next_id)))

    keyboard = InlineKeyboardMarkup()
    keyboard.insert(url)
    keyboard.row(*line)
    return keyboard


def keyboard_catalog(_list: list):
    """ Начальная клавиатура для переходу к основному каталогу """
    if len(_list) == 0:
        return InlineKeyboardMarkup().add(
            InlineKeyboardButton("Каталог пуст! Перейти на сайт", url="https://example.com/")
        )
    first_sofa = str(_list[0])
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton("К каталогу диванов!!!", callback_data=first_sofa)
    )
