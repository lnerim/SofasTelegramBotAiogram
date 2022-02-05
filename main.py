from aiogram import Bot, Dispatcher, executor, types
from os import getenv

from aiogram.types.base import InputFile

from keyboards import keyboard_sofa

bot = Bot(token=getenv("TOKEN_TG"))
dp = Dispatcher(bot)


@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    await message.answer("Привет!\nХочешь купить диван? Тебе к нам!")


@dp.message_handler(commands=["help"])
async def cmd_help(message: types.Message):
    await message.answer("Я тут, чтобы помочь тебе!", reply_markup=keyboard_sofa(0, 1))


@dp.message_handler()
async def echo(message: types.Message):
    if message.text[:1] == "/":
        return await message.answer("Ой, не знаю такую команду!")
    await message.answer("Я не понимаю тебя...")


@dp.callback_query_handler()
async def process_callback_kb1btn1(callback_query: types.CallbackQuery):
    photo = open("image.png")
    await bot.send_photo(callback_query.message.chat.id, photo=photo)
    await callback_query.message.answer(callback_query.data)
    await callback_query.answer()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
