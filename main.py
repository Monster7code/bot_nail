import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from aiogram import F
from keyboards import *
from states import *
import os
from conec import token

bot = Bot(token)
loop = asyncio.get_event_loop()
dp = Dispatcher(Bot=bot, loop=loop, storage=MemoryStorage())


async def start():
    try:
        await dp.start_polling(bot)

    finally:
        await bot.session.close()
        return dp


@dp.message(Command("start"))
async def any_message(message: Message, state: FSMContext):

    text = ("Доброго времени суток, я - мастер 'Имя'!\n"
            "С помощью этого бота вы сможете:\n"
            "🔶 Записаться на процедуры,\n"
            "🔶 Ознакомиться с моими услугами,\n"
            "🔶 Подобрать дизайн маникюра")

    await bot.send_photo(chat_id=message.from_user.id,
                         photo=types.FSInputFile(path="images/main.jpg"),
                         caption=text,
                         reply_markup=start_keyboard.as_markup(resize_keyboard=True))


@dp.callback_query(lambda call: call.data == "sign_up_service")
async def sign_up_service(call: types.CallbackQuery, state: FSMContext):
    servise= {
        "Понедельник": ["11:00", "12:00", "13:00"],
        "Вторник": ["13:00", "14:00"]
    }
    for day in servise.keys():
        await call.message.answer(f"{day}", reply_markup=generate_signup_keyboard(servise[day]).as_markup())


@dp.callback_query(lambda call: call.data == "palette_colors")
async def palette_colors(call: types.CallbackQuery, state: FSMContext):

    directory = "C:/Users/admin/PycharmProjects/bot_nail/images/palette"
    files = os.listdir(directory)
    for image in files:

        await bot.send_photo(chat_id=call.from_user.id,
                             photo=types.FSInputFile(path=f"images/palette/{image}"))

    await call.message.answer(text="Главная", reply_markup=start_keyboard.as_markup(resize_keyboard=True))


@dp.callback_query(lambda call: call.data == "info_service")
async def info_service(call: types.CallbackQuery, state: FSMContext):
    text = ("Все инструменты обрабатываются перед каждым использованием,\n"
            "Используеться только проверенная продукция.")
    await bot.send_photo(chat_id=call.from_user.id,
                         photo=types.FSInputFile(path=f"images/clear.jpg"), caption=text,
                         reply_markup=start_keyboard.as_markup(resize_keyboard=True))


@dp.callback_query(lambda call: call.data == "info")
async def info(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Всю следующую неделю скидка 21%!!!",
                              reply_markup=start_keyboard.as_markup(resize_keyboard=True))


@dp.callback_query(lambda call: call.data == "choice_design")
async def choice_design(call: types.CallbackQuery, state: FSMContext):

    await call.message.answer("Пройдите тест для выбора подходящего дизайна!",
                              reply_markup=types.ReplyKeyboardRemove())
    query_set = [
        ["Выберите занятие:", "уборка", "готовка", "стирка", "помыть посуду"],
        ["Выберите животное:", "лиса", "пантера", "крыса", "жираф"]
    ]
    await state.set_data({"query_set": query_set, "index": 1, "result": 0})
    await call.message.answer(query_set[0][0],
                              reply_markup=generate_keyboard(query_set[0][1:]).as_markup(resize_keyboard=True))


@dp.callback_query(lambda call: (call.data == "first_answer") or (call.data == "second_answer") or
                                (call.data == "third_answer") or (call.data == "fourth_answer"))
async def first_answer(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    index = data.get("index")
    question = data.get("query_set")
    result = data.get("result")
    add_index = 0
    if call.data == "first_answer":
        add_index = 1
    elif call.data == "second_answer":
        add_index = 2
    elif call.data == "third_answer":
        add_index = 3
    elif call.data == "fourth_answer":
        add_index = 5

    res = result + add_index
    await state.update_data(result=res)

    if check_on_end(question, index):
        data = await state.get_data()
        result = data.get("result")

        await send_message(call.from_user.id, result)
    else:
        await state.update_data(index=index + 1)

        await call.message.answer(question[index][0],
                                  reply_markup=generate_keyboard(question[index][1:]).as_markup(resize_keyboard=True))


def check_on_end(question, index):
    if len(question) == index:
        return True
    else:
        return False


async def send_message(user_id, result):
    image = ""

    if result < 4:
        image = f"images/design/first.jpg"

    elif (result > 4) and (result <= 8):
        image = f"images/design/second.jpg"

    elif (result > 8) and (result <= 12):
        image = f"images/design/third.jpg"

    elif (result > 12) and (result <= 16):
        image = f"images/design/fourth.jpg"

    await bot.send_photo(chat_id=user_id,
                         photo=types.FSInputFile(path=image), caption="Вам подходит",
                         reply_markup=start_keyboard.as_markup(resize_keyboard=True))


@dp.callback_query(lambda call: call.data[:7] == "sign_up")
async def sign_up(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer(f"Вы записались на {call.message.text}\nМастер скоро свяжеться с вами")
    await bot.send_message(chat_id="5805700754", text=f'Новая запись в {call.message.text}\n'
                                                      f'На {call.data.split("|")[1]}'
                                                           f'\nПользователь: <a href="{call.from_user.url}">{call.from_user.username}</a>\n'
                           , parse_mode="html")


if __name__ == "__main__":
    asyncio.run(start())
