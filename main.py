from aiogram import Bot, Dispatcher, executor, types
from os import getenv
from database import BotDB

from keyboards import *

bot = Bot(token=getenv("TOKEN_TG"))
dp = Dispatcher(bot)
bot_db = BotDB("bot.sqlite3")


@dp.message_handler(commands=["start", "help"])
async def send_welcome(message: types.Message):
    await message.answer(
        f"Привет, {message.chat.first_name}!\n"
        f"Хочешь купить диван? Тебе к нам!", reply_markup=keyboard_catalog())


@dp.message_handler()
async def echo(message: types.Message):
    if message.text[:1] == "/":
        return await message.answer("Ой, не знаю такую команду!")
    await message.answer("Я не понимаю тебя...")


@dp.callback_query_handler()
async def callback_sofa(callback_query: types.CallbackQuery):
    sofa = bot_db.get_sofa(callback_query.data)
    if sofa is not None:
        id_sofa, name, price, picture = sofa

        await callback_query.message.delete()
        await bot.send_photo(
            chat_id=callback_query.message.chat.id,
            photo=picture,
            caption=name,
            reply_markup=keyboard_sofa(
                back_id=None if not bot_db.get_sofa(id_sofa-1) else id_sofa-1,  # Если диванов с крайними к нему
                next_id=None if not bot_db.get_sofa(id_sofa+1) else id_sofa+1,  # индексами нет, то кнопка убирается
                price=price)
        )
    else:
        await callback_query.answer(text=f"Дивана с таким индексом нет -> {callback_query.data}", show_alert=True)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
