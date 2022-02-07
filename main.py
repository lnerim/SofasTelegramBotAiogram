from os import getenv

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from database import BotDB
from keyboards import *

bot = Bot(token=getenv("TOKEN_TG"))
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
bot_db = BotDB("bot.sqlite3")
admin = int(getenv("ID_ADMIN"))


@dp.message_handler(commands=["start", "help"])
async def cmd_start(message: types.Message):
    await message.answer(
        f"Привет, {message.chat.first_name}!\n"
        f"Хочешь купить диван? Тебе к нам!\n",
        reply_markup=keyboard_catalog())


@dp.message_handler(commands=["location"])
async def cmd_location(message: types.Message):
    await message.answer("Мы находимся здесь ⤵")
    await bot.send_location(message.chat.id, 55.755696, 37.617306)  # Москва


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
                back_id=None if not bot_db.get_sofa(id_sofa - 1) else id_sofa - 1,  # Если диванов с крайними к нему
                next_id=None if not bot_db.get_sofa(id_sofa + 1) else id_sofa + 1,  # индексами нет, то кнопка убирается
                price=price
            )
        )
    else:
        await callback_query.answer(text=f"Дивана с таким индексом нет -> {callback_query.data}", show_alert=True)


# Админ часть
class Form(StatesGroup):
    name = State()
    price = State()
    image = State()


@dp.message_handler(lambda message: message.chat.id == admin, commands=["new_sofa"])
async def cmd_new_sofa(message: types.Message):
    await Form.name.set()
    await message.answer("Введите имя дивана.")


@dp.message_handler(state='*', commands='cancel')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return await message.reply("Никаких действий нет.")
    await state.finish()
    await message.reply("Действие отменено!")


@dp.message_handler(state=Form.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await Form.next()
    await message.answer("Отлично! Укажите его цену.")


@dp.message_handler(state=Form.price)
async def process_age(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        await Form.next()
        await state.update_data(price=int(message.text))
        await message.reply("Хорошо, теперь картинку этого дивана.")
    else:
        await message.reply("Неверно! Укажите число!")


@dp.message_handler(state=Form.image)
async def process_gender_invalid(message: types.Message):
    await message.reply("Принимаются только картинки!")


@dp.message_handler(state=Form.image, content_types=["photo"])
async def process_gender(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        my_file_id = message.photo[-1].file_id
        my_file = await bot.download_file_by_id(file_id=my_file_id)
        bot_db.new_sofa(**data, image=my_file.read())
        await message.answer("Успешно создано!")
    await state.finish()


@dp.message_handler()
async def echo(message: types.Message):
    if message.text[:1] == "/":
        return await message.answer("Ой, такой команды нет!")
    await message.answer("Я не понимаю тебя...\nТебе поможет - /help")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
