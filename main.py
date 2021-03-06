from asyncio import sleep
from os import getenv

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.exceptions import MessageTextIsEmpty

from database import BotDB
from keyboards import *

bot = Bot(token=getenv("TOKEN_TG"))
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
bot_db = BotDB("bot.sqlite3")
admins = [int(getenv("ID_ADMIN"))]


@dp.message_handler(commands=["start", "help"])
async def cmd_start(message: types.Message):
    await bot.set_my_commands([
        types.BotCommand("start", "Старт бота"),
        types.BotCommand("location", "Наше местоположение"),
    ])

    sticker = await message.answer_sticker("CAACAgIAAxkBAAIDIGIBeUKI5I4VBdKGiNlbJzMuOF_qAALGAQACFkJrCkoj1PTJ23lHIwQ")
    await message.answer(
        f"Привет, {message.chat.first_name}!\n"
        f"Мы представляем компанию по продаже диванов!\n"
        f"Вы можете выбрать любой диван и заказать его в один клик!\n"
        f"Купить диван? Тебе к нам!\n",
        reply_markup=keyboard_catalog(bot_db.all_id_sofa()))
    await sleep(3)
    await bot.delete_message(message.chat.id, sticker.message_id)


@dp.message_handler(commands=["location"])
async def cmd_location(message: types.Message):
    await message.answer("Мы находимся здесь ⤵")
    await bot.send_location(message.chat.id, 55.755696, 37.617306)  # Москва


@dp.callback_query_handler()
async def callback_sofa(callback_query: types.CallbackQuery):
    sofa = bot_db.get_sofa(callback_query.data)
    if sofa is not None:
        id_sofa, name, price, picture = sofa
        all_id_sofa = bot_db.all_id_sofa()
        index = all_id_sofa.index(id_sofa)

        back_id = None if index - 1 < 0 else all_id_sofa[index - 1]
        next_id = None if index >= len(all_id_sofa)-1 else all_id_sofa[index + 1]

        await callback_query.message.delete()
        await bot.send_photo(
            chat_id=callback_query.message.chat.id,
            photo=picture,
            caption=name,
            reply_markup=keyboard_sofa(back_id, next_id, price)
        )
    else:
        await callback_query.answer(text=f"Дивана с таким индексом нет -> {callback_query.data}", show_alert=True)


# Админ часть
class Form(StatesGroup):
    name = State()
    price = State()
    image = State()


# Admin command
@dp.message_handler(lambda message: message.chat.id in admins, commands=["new_sofa"])
async def cmd_new_sofa(message: types.Message):
    await Form.name.set()
    await message.answer("Введите имя дивана.\nОтмена - /cancel")


# Выход из машины состояний
@dp.message_handler(state='*', commands='cancel')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return await message.reply("Никаких действий нет.")
    await state.finish()
    await message.reply("Действие отменено!")


@dp.message_handler(state=Form.name)
async def set_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await Form.next()
    await message.answer("Отлично! Укажите его цену.\nОтмена - /cancel")


@dp.message_handler(state=Form.price)
async def set_price(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        await Form.next()
        await state.update_data(price=int(message.text))
        await message.reply("Хорошо, теперь картинку этого дивана.\nОтмена - /cancel")
    else:
        await message.reply("Неверно! Укажите число!\nОтмена - /cancel")


@dp.message_handler(state=Form.image)
async def set_image_error(message: types.Message):
    await message.reply("Принимаются только картинки!\nОтмена - /cancel")


@dp.message_handler(state=Form.image, content_types=["photo"])
async def set_image(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        my_file_id = message.photo[-1].file_id
        my_file = await bot.download_file_by_id(file_id=my_file_id)
        bot_db.new_sofa(**data, image=my_file.read())
        await message.answer("Успешно создано!")
    await state.finish()


# Admin command
@dp.message_handler(lambda message: message.chat.id in admins, commands=["delete"])
async def cmd_delete(message: types.message):
    try:
        id_sofa = message.get_args()
        id_sofa = int(id_sofa)
        if bot_db.get_sofa(id_sofa):
            bot_db.delete_sofa(id_sofa)
            await message.answer("Диван удалён!")
        else:
            await message.reply("Такого дивана нет!")
    except (MessageTextIsEmpty,  ValueError):  # Пустое сообщение, либо не число
        await message.reply("Укажите id: /delete <id: int>")


@dp.message_handler()
async def echo(message: types.Message):
    if message.text[:1] == "/":
        return await message.answer("Ой, такой команды нет!\nСписок команд - /help")
    await message.answer("Я не понимаю тебя...\nТебе поможет - /help")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
