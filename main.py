import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from aiogram import F
from keyboards import *
from states import *
import os
from conec import token
from conec_bd import connect_db
from request_db import *
from schedule_nail import *

bot = Bot(token)
loop = asyncio.get_event_loop()
dp = Dispatcher(Bot=bot, loop=loop, storage=MemoryStorage())
conn = connect_db()
admin_tg_id = "6259845330"

def get_conn():
    return conn


async def start():
    try:
        await dp.start_polling(bot)

    finally:
        await bot.session.close()
        return dp


@dp.message(Command("start"))
async def any_message(message: Message, state: FSMContext):
    text = get_start_message(conn, admin_tg_id)

    await bot.send_photo(chat_id=message.from_user.id,
                         photo=types.FSInputFile(path="images/main.jpg"),
                         caption=text,
                         reply_markup=create_start_keyboard().as_markup(resize_keyboard=True))


@dp.callback_query(lambda call: call.data == "sign_up_service")
async def sign_up_service(call: types.CallbackQuery, state: FSMContext):
    text = ""
    index = 0
    for date in get_dates():
        text += f"/{index} --- посмотреть свободные места на дату {date}\n"
        index += 1

    await call.message.answer(text, reply_markup=ReplyKeyboardRemove())


@dp.callback_query(lambda call: call.data == "palette_colors")
async def palette_colors(call: types.CallbackQuery, state: FSMContext):

    directory = "C:/Users/admin/PycharmProjects/bot_nail/images/palette"
    files = os.listdir(directory)
    for image in files:

        await bot.send_photo(chat_id=call.from_user.id,
                             photo=types.FSInputFile(path=f"images/palette/{image}"))

    await call.message.answer(text="Главная", reply_markup=create_start_keyboard().as_markup(resize_keyboard=True))


@dp.callback_query(lambda call: call.data == "info_service")
async def info_service(call: types.CallbackQuery, state: FSMContext):
    text = get_info_service_message(conn, admin_tg_id)
    await bot.send_photo(chat_id=call.from_user.id,
                         photo=types.FSInputFile(path=f"images/clear.jpg"), caption=text,
                         reply_markup=create_start_keyboard().as_markup(resize_keyboard=True))
    await call.answer()


@dp.callback_query(lambda call: call.data == "info")
async def info(call: types.CallbackQuery, state: FSMContext):
    text = get_current_informathion_message(conn, admin_tg_id)
    await call.message.answer(text,
                              reply_markup=create_start_keyboard().as_markup(resize_keyboard=True))
    await call.answer()


@dp.callback_query(lambda call: call.data == "choice_design")
async def choice_design(call: types.CallbackQuery, state: FSMContext):

    await call.message.answer("Пройдите тест для выбора подходящего дизайна!",
                              reply_markup=types.ReplyKeyboardRemove())
    if get_design_test(conn, admin_tg_id):
        query_set = get_design_test(conn, admin_tg_id)
        print(query_set)
        await state.set_data({"query_set": query_set, "index": 1, "result": 0})
        await call.message.answer(query_set[0][0],
                                  reply_markup=generate_keyboard(query_set[0][1:]).as_markup(resize_keyboard=True))

    else:
        await call.message.answer("На данный момент тест не доступен.")
        text = get_start_message(conn, admin_tg_id)

        await bot.send_photo(chat_id=call.from_user.id,
                             photo=types.FSInputFile(path="images/main.jpg"),
                             caption=text,
                             reply_markup=create_start_keyboard().as_markup(resize_keyboard=True))
    await call.answer()


@dp.callback_query(lambda call: (call.data == "first_answer") or (call.data == "second_answer") or
                                (call.data == "third_answer") or (call.data == "fourth_answer"))
async def first_answer(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.delete()
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
        await state.clear()
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
    if result <= 4:
        image = f"images/design/first.jpg"

    elif (result > 4) and (result <= 8):
        image = f"images/design/second.jpg"

    elif (result > 8) and (result <= 12):
        image = f"images/design/third.jpg"

    elif (result > 12) and (result <= 16):
        image = f"images/design/fourth.jpg"

    await bot.send_photo(chat_id=user_id,
                         photo=types.FSInputFile(path=image), caption="Вам подходит",
                         reply_markup=create_start_keyboard().as_markup(resize_keyboard=True))


# Запись на услуги
#
#
@dp.message(Command(*[str(i) for i in range(0, 51)]))
async def write_on_nail(message: Message, state: FSMContext):
    list_times = get_info()
    day = list_times[int(message.text[1:])]
    await state.update_data(index_day=int(message.text[1:]))
    await message.answer(f"{day[0]}", reply_markup=generate_signup_keyboard(day[1:]).as_markup())


@dp.callback_query(lambda call: (call.data[:7] == "sign_up") or (call.data == "back_time"))
async def sign_up(call: types.CallbackQuery, state: FSMContext):
    if call.data == "back_time":
        await call.message.delete()
        text = ""
        index = 0
        for date in get_dates():
            text += f"/{index} --- посмотреть свободные места на дату {date}\n"
            index += 1

        await call.message.answer(text, reply_markup=ReplyKeyboardRemove())
    else:
        await call.message.delete()
        await state.update_data(date=call.message.text)
        await state.update_data(time=call.data.split("|")[1])
        await call.message.answer(f"Вы хотите записаться на {call.message.text} в {call.data.split("|")[1]}"
                                    f"\nПожалуйста выберите услугу",
                                    reply_markup=create_service_keyboard(conn, admin_tg_id).as_markup())


@dp.callback_query(lambda call: (call.data[:14] == "choice_service") or (call.data == "back_to_day"))
async def sign_up(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if call.data == "back_to_day":
        await call.message.delete()
        data = await state.get_data()
        index_day = data.get("index_day")
        list_times = get_info()
        day = list_times[int(index_day)]
        await bot.send_message(chat_id=call.from_user.id, text=f"{day[0]}",
                               reply_markup=generate_signup_keyboard(day[1:]).as_markup())

    else:
        await call.message.delete()
        day = data.get("date")
        time = data.get("time")
        await call.message.answer(f"Вы записались на {day} в {time}"
                                  f"\nНа услугу {call.data.split("|")[1]}",
                                  reply_markup=create_start_keyboard().as_markup())

        await bot.send_message(chat_id="5805700754", text=f'Новая запись в {time}\n'
                                                          f'На {day}, услуга: {call.data.split("|")[1]}'
                                                               f'\nПользователь: <a href="{call.from_user.url}">{call.from_user.username}</a>\n'
                               , parse_mode="html")
        if create_recording(day, time, str(call.from_user.url)):
            await bot.send_message(chat_id="5805700754", text=f'Новая запись в занесена в таблицу\n')
        else:
            await bot.send_message(chat_id="5805700754", text=f'Возникли проблемы при записи в таблицу\n'
                                                             f'Обратитесь в техподдержку!')
        await state.clear()
# Админка
#
#


@dp.message(Command("admin"))
async def any_message(message: Message, state: FSMContext):
    if check_on_admin(conn, message.from_user.id):

        text = "Вы перешли в админ панель"
        keyboard = admin_keyboard
        await state.set_state(AdminState.change)
        image = "admin.jpg"
    else:
        text = "В доступе отказано"
        keyboard = create_start_keyboard()
        image = "main.jpg"

    await bot.send_photo(chat_id=message.from_user.id,
                         photo=types.FSInputFile(path=f"images/{image}"),
                         caption=text,
                         reply_markup=keyboard.as_markup(resize_keyboard=True))


@dp.message(AdminState.change)
async def changer(message: Message, state: FSMContext):
    if message.text.lower() == "поменять приветственное сообщение":
        await state.set_state(AdminState.change_main)
        text = "На данный момент стартовое сообщение выглядит так:\n" + get_start_message(conn, admin_tg_id)
        await bot.send_photo(chat_id=message.from_user.id,
                             photo=types.FSInputFile(path="images/main.jpg"),
                             caption=text,
                             reply_markup=keyboard_swap_main.as_markup(resize_keyboard=True))
    elif message.text.lower() == "назад":
        await message.answer("Вы вернулись в главное меню", reply_markup=ReplyKeyboardRemove())
        await state.clear()
        text = get_start_message(conn, admin_tg_id)

        await bot.send_photo(chat_id=message.from_user.id,
                             photo=types.FSInputFile(path="images/main.jpg"),
                             caption=text,
                             reply_markup=create_start_keyboard().as_markup(resize_keyboard=True))
    elif message.text.lower() == "поменять информацию об услугах":
        await state.set_state(AdminState.change_info_service)
        text = ("На данный момент информация об услугах выглядит так:\n"
                + get_info_service_message(conn, admin_tg_id))
        await bot.send_photo(chat_id=message.from_user.id,
                             photo=types.FSInputFile(path="images/clear.jpg"),
                             caption=text,
                             reply_markup=keyboard_swap_main.as_markup(resize_keyboard=True))
    elif message.text.lower() == "редактировать услуги":
        await state.set_state(AdminState.change_service)
        await message.answer("Услуги которые вы предоставляете")
        services = get_master_service(conn, admin_tg_id)
        for service in services:
            await message.answer(f"{service[0]}", reply_markup=create_drop_service_keyboard(service[0]).as_markup())
        await message.answer(f"Чтобы добавить новую услугу, напишите её название",
                             reply_markup=default_keyboard.as_markup())

    elif message.text.lower() == "редактировать палитру цветов":
        directory = "C:/Users/admin/PycharmProjects/bot_nail/images/palette"
        await state.set_state(AdminState.change_palette)
        await message.answer("Ваша палитра цветов:")
        files = os.listdir(directory)
        for image in files:
            await bot.send_photo(chat_id=message.from_user.id,
                                 photo=types.FSInputFile(path=f"images/palette/{image}"),
                                 reply_markup=create_drop_palette_keyboard(image).as_markup())

        await message.answer(f"Чтобы добавить новую цвет в палитру, отправте фото(по одному)",
                             reply_markup=default_keyboard.as_markup())

    elif message.text.lower() == "редактировать актуальную информацию":
        await state.set_state(AdminState.current_informathion)
        text = ("На данный момент актуальная информация выглядит так:\n"
                + get_current_informathion_message(conn, admin_tg_id))
        await bot.send_photo(chat_id=message.from_user.id,
                             photo=types.FSInputFile(path="images/main.jpg"),
                             caption=text,
                             reply_markup=default_keyboard.as_markup())
        await message.answer('Для смены текста "актульной информации", отправте боту готовый текст')

    elif message.text.lower() == "редактировать ссылки на социальные сети":
        await state.set_state(AdminState.social_links)
        await message.answer("Выберите социальную сеть:", reply_markup=social_links_keyboard.as_markup())

    elif message.text.lower() == "редактировать тест для выбора дизайна":
        await state.set_state(AdminState.access_change_test)
        await message.answer("Тест состоит из неограниченного количества вопросов и четырёх вариантов ответа.\n"
                             "Каждый вариант ответа имеет коэфициент, первый вариант ответа имеет наименьший.\n"
                             "После прохождения теста, варианты ответа будут подсчитаны и будет выдан дизайн исходя из "
                             "итоговой суммы ответов.\n"
                             "Предлагаемые дизайны вы можете поменять кнопкой ниже, самая первая картинка имеет"
                             " наименьший вес при подсчете резёльтата")
        await message.answer("<b>Обращаем ваше внимание</b>, что при создании <b>нового теста</b>,"
                             " <b>старый тест удаляется</b>.\n"
                             "С уважением администрация horizont_edge",
                             reply_markup=access_change_test_keyboard.as_markup(), parse_mode="html")


@dp.callback_query(lambda call: (call.data[:12] == "drop_service"))
async def drop_service(call: types.CallbackQuery, state: FSMContext):

    if delete_service_master(conn, call.data.split("|")[1], admin_tg_id):
        await bot.send_message(chat_id=call.from_user.id, text=f"Вы удалили услугу: {call.data.split("|")[1]}",
                               reply_markup=default_keyboard.as_markup())
        await call.message.delete()
    else:
        await bot.send_message(chat_id=call.from_user.id, text=f"При удалении услуги произошла ошибка"
                                                               f" обратитесь в техподдежку",
                               reply_markup=default_keyboard.as_markup())


@dp.message(AdminState.change_service)
async def add_service(message: Message, state: FSMContext):
    if message.text == "Назад":
        text = "Вы перешли в админ панель"
        keyboard = admin_keyboard
        await state.set_state(AdminState.change)
        await bot.send_photo(chat_id=message.from_user.id,
                             photo=types.FSInputFile(path="images/admin.jpg"),
                             caption=text,
                             reply_markup=keyboard.as_markup(resize_keyboard=True))
    else:
        name_service = message.text
        if append_service(conn, name_service, admin_tg_id):
            await message.answer(text=f"Вы успешно добавили услугу: {name_service}",
                                 reply_markup=default_keyboard.as_markup())
            await message.answer("Услуги которые вы предоставляете")
            services = get_master_service(conn, admin_tg_id)
            for service in services:
                await message.answer(f"{service[0]}",
                                     reply_markup=create_drop_service_keyboard(service[0]).as_markup())
        else:
            await message.answer(text=f"При добавлении услуги произошла ошибка"
                                      f" обратитесь в техподдежку",
                                 reply_markup=default_keyboard.as_markup())


@dp.callback_query(lambda call: (call.data[:12] == "change_image"))
async def change_image(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(AdminState.change_image_design)
    await call.message.delete()
    await bot.send_message(chat_id=call.from_user.id, text="Для смены картинки отправте боту новую картинку",
                           reply_markup=default_keyboard.as_markup())
    await state.update_data(name_file=call.data.split("|")[1])


@dp.message(AdminState.change_image_design)
async def change_image_design(message: Message, state: FSMContext):
    if message.text == "Назад":
        text = "Вы перешли в админ панель"
        keyboard = admin_keyboard
        await state.set_state(AdminState.change)
        await bot.send_photo(chat_id=message.from_user.id,
                             photo=types.FSInputFile(path="images/admin.jpg"),
                             caption=text,
                             reply_markup=keyboard.as_markup(resize_keyboard=True))
    else:
        if message.photo:
            try:
                data = await state.get_data()
                name_file = data.get("name_file")
                directory = "C:/Users/admin/PycharmProjects/bot_nail/images/design/"
                file_name = f"{directory}/{name_file}"
                await bot.download(message.photo[-1], destination=file_name)
                await bot.send_message(chat_id=message.from_user.id, text=f"Вы сменили дизайн",
                                       reply_markup=default_keyboard.as_markup())
            except:
                await bot.send_message(chat_id=message.from_user.id, text=f"При замене картинки произошла ошибка"
                                                                       f" обратитесь в техподдежку",
                                       reply_markup=default_keyboard.as_markup())


'''@dp.message(AdminState.change_palette)
async def add_service(message: Message, state: FSMContext):
    if message.text == "Назад":
        text = "Вы перешли в админ панель"
        keyboard = admin_keyboard
        await state.set_state(AdminState.change)
        await bot.send_photo(chat_id=message.from_user.id,
                             photo=types.FSInputFile(path="images/admin.jpg"),
                             caption=text,
                             reply_markup=keyboard.as_markup(resize_keyboard=True))'''


@dp.callback_query(lambda call: (call.data[:10] == "drop_image"))
async def drop_image(call: types.CallbackQuery, state: FSMContext):
    try:
        name_file = call.data.split("|")[1]
        directory = "C:/Users/admin/PycharmProjects/bot_nail/images/palette/"
        os.remove(f"{directory}/{name_file}")
        await bot.send_message(chat_id=call.from_user.id, text=f"Вы удалили палитру",
                               reply_markup=default_keyboard.as_markup())
        await call.message.delete()
    except:
        await bot.send_message(chat_id=call.from_user.id, text=f"При удалении палитры произошла ошибка"
                                                               f" обратитесь в техподдежку",
                               reply_markup=default_keyboard.as_markup())


@dp.message(AdminState.change_palette)
async def add_service(message: Message, state: FSMContext):
    if message.text == "Назад":
        text = "Вы перешли в админ панель"
        keyboard = admin_keyboard
        await state.set_state(AdminState.change)
        await bot.send_photo(chat_id=message.from_user.id,
                             photo=types.FSInputFile(path="images/admin.jpg"),
                             caption=text,
                             reply_markup=keyboard.as_markup(resize_keyboard=True))
    else:
        if message.photo:
            try:
                directory = "C:/Users/admin/PycharmProjects/bot_nail/images/palette"
                file_name = f"{directory}/{message.photo[-1].file_unique_id}.jpg"
                await bot.download(message.photo[-1], destination=file_name)
                await message.answer("Вы успешно добавили цвет")

                await message.answer("Ваша палитра цветов:")
                files = os.listdir(directory)
                for image in files:
                    await bot.send_photo(chat_id=message.from_user.id,
                                         photo=types.FSInputFile(path=f"images/palette/{image}"),
                                         reply_markup=create_drop_palette_keyboard(image).as_markup())
            except:
                await message.answer(text=f"При добавлении цвета произошла ошибка (возможно вы пытаетесь удалить уже"
                                          f" не существующее изображение)"
                                          f" обратитесь в техподдежку",
                                     reply_markup=default_keyboard.as_markup())
        else:
            await message.answer(text=f"Пожалуйста добавте одно изображение "
                                      f"не нажимая на кнопку сжать изображение",
                                 reply_markup=default_keyboard.as_markup())


@dp.message(AdminState.current_informathion)
async def change_main_text(message: Message, state: FSMContext):
    if len(message.text) == 0:
        text = "Пожалуйста введите корректный текст"
        await message.answer(text, reply_markup=default_keyboard.as_markup())
    elif message.text == "Назад":
        text = "Вы перешли в админ панель"
        keyboard = admin_keyboard
        await state.set_state(AdminState.change)
        await bot.send_photo(chat_id=message.from_user.id,
                             photo=types.FSInputFile(path="images/admin.jpg"),
                             caption=text,
                             reply_markup=keyboard.as_markup(resize_keyboard=True))
    else:
        if set_new_current_informathion_text(conn, admin_tg_id, message.text):
            await message.answer("Вы успешно поменяли актульную информацию")
            text = ("На данный момент актуальная информация выглядит так:\n"
                    + get_current_informathion_message(conn, admin_tg_id))
            await bot.send_photo(chat_id=message.from_user.id,
                                 photo=types.FSInputFile(path="images/main.jpg"),
                                 caption=text,
                                 reply_markup=default_keyboard.as_markup(resize_keyboard=True))
        else:
            await message.answer(text=f"При изменении актуальной информации произошла ошибка."
                                      f" Обратитесь в техподдежку",
                                 reply_markup=default_keyboard.as_markup())


@dp.message(AdminState.change_main)
async def change_main(message: Message, state: FSMContext):
    if message.text.lower() == "поменять текст":
        await state.set_state(AdminState.change_main_text)
        text = "Введите новый текст"
        await message.answer(text, reply_markup=ReplyKeyboardRemove())
    elif message.text.lower() == "поменять картинку":
        await state.set_state(AdminState.change_main_image)
        text = "Отправте новую картинку"
        await message.answer(text, reply_markup=ReplyKeyboardRemove())

    elif message.text == "Назад":
        text = "Вы перешли в админ панель"
        keyboard = admin_keyboard
        await state.set_state(AdminState.change)
        await bot.send_photo(chat_id=message.from_user.id,
                             photo=types.FSInputFile(path="images/admin.jpg"),
                             caption=text,
                             reply_markup=keyboard.as_markup(resize_keyboard=True))


@dp.message(AdminState.change_main_text)
async def change_main_text(message: Message, state: FSMContext):
    if len(message.text) == 0:
        text = "Пожалуйста введите корректный текст"
        await message.answer(text, reply_markup=ReplyKeyboardRemove())
    else:
        set_new_main_text(conn, admin_tg_id, message.text)
        await message.answer("Вы успешно поменяли текст")
        await state.set_state(AdminState.change_main)
        text = "На данный момент стартовое сообщение выглядит так:\n" + get_start_message(conn, admin_tg_id)
        await bot.send_photo(chat_id=message.from_user.id,
                             photo=types.FSInputFile(path="images/main.jpg"),
                             caption=text,
                             reply_markup=keyboard_swap_main.as_markup(resize_keyboard=True))


@dp.message(AdminState.change_main_image)
async def change_main_image(message: Message, state: FSMContext):
    if message.photo:
        file_name = f"images/main.jpg"
        await bot.download(message.photo[-1], destination=file_name)
        await message.answer("Вы успешно поменяли фото")
        await state.set_state(AdminState.change_main)
        text = "На данный момент стартовое сообщение выглядит так:\n" + get_start_message(conn, admin_tg_id)
        await bot.send_photo(chat_id=message.from_user.id,
                             photo=types.FSInputFile(path="images/main.jpg"),
                             caption=text,
                             reply_markup=keyboard_swap_main.as_markup(resize_keyboard=True))


@dp.message(AdminState.change_info_service)
async def change_info_service(message: Message, state: FSMContext):
    if message.text.lower() == "поменять текст":
        await state.set_state(AdminState.change_info_service_text)
        text = "Введите новый текст"
        await message.answer(text, reply_markup=ReplyKeyboardRemove())
    elif message.text.lower() == "поменять картинку":
        await state.set_state(AdminState.change_info_service_image)
        text = "Отправте новую картинку"
        await message.answer(text, reply_markup=ReplyKeyboardRemove())

    elif message.text == "Назад":
        text = "Вы перешли в админ панель"
        keyboard = admin_keyboard
        await state.set_state(AdminState.change)
        await bot.send_photo(chat_id=message.from_user.id,
                             photo=types.FSInputFile(path="images/admin.jpg"),
                             caption=text,
                             reply_markup=keyboard.as_markup(resize_keyboard=True))


@dp.message(AdminState.change_info_service_text)
async def change_info_service_text(message: Message, state: FSMContext):
    if len(message.text) == 0:
        text = "Пожалуйста введите корректный текст"
        await message.answer(text, reply_markup=ReplyKeyboardRemove())
    else:
        set_new_info_service_text(conn, admin_tg_id, message.text)
        await message.answer("Вы успешно поменяли текст")
        await state.set_state(AdminState.change_main)
        text = ("На данный момент информация об услугах выглядит так:\n"
                + get_info_service_message(conn, admin_tg_id))
        await bot.send_photo(chat_id=message.from_user.id,
                             photo=types.FSInputFile(path="images/clear.jpg"),
                             caption=text,
                             reply_markup=keyboard_swap_main.as_markup(resize_keyboard=True))


@dp.message(AdminState.change_info_service_image)
async def change_info_service_image(message: Message, state: FSMContext):
    if message.photo:
        file_name = f"images/clear.jpg"
        await bot.download(message.photo[-1], destination=file_name)
        await message.answer("Вы успешно поменяли фото")
        await state.set_state(AdminState.change_main)
        text = "На данный момент информация об услугах выглядит так:\n" + get_start_message(conn, admin_tg_id)
        await bot.send_photo(chat_id=message.from_user.id,
                             photo=types.FSInputFile(path="images/clear.jpg"),
                             caption=text,
                             reply_markup=keyboard_swap_main.as_markup(resize_keyboard=True))


@dp.message(AdminState.social_links)
async def social_links(message: Message, state: FSMContext):
    if message.text.lower() == "инстаграм":
        await state.update_data(name_link="инстаграм")
        await state.set_state(AdminState.change_link)
        text = "Введите новую ссылку"
        await message.answer(text, reply_markup=default_keyboard.as_markup())
    elif message.text.lower() == "вконтакте":
        await state.set_state(AdminState.change_link)
        await state.update_data(name_link="вконтакте")
        text = "Введите новую ссылку"
        await message.answer(text, reply_markup=default_keyboard.as_markup())

    elif message.text == "Назад":
        text = "Вы перешли в админ панель"
        keyboard = admin_keyboard
        await state.set_state(AdminState.change)
        await bot.send_photo(chat_id=message.from_user.id,
                             photo=types.FSInputFile(path="images/admin.jpg"),
                             caption=text,
                             reply_markup=keyboard.as_markup(resize_keyboard=True))


@dp.message(AdminState.change_link)
async def change_link(message: Message, state: FSMContext):
    if message.text == "Назад":
        await state.set_state(AdminState.social_links)
        await message.answer("Выберите социальную сеть:", reply_markup=social_links_keyboard.as_markup())
    else:
        data = await state.get_data()
        name_link = data.get("name_link")
        if set_social_link(conn, name_link, message.text, admin_tg_id):
            await message.answer(f"Вы успешно поменяли сслыку для {name_link}")
            await state.set_state(AdminState.social_links)
            await message.answer("Выберите социальную сеть:", reply_markup=social_links_keyboard.as_markup())
        else:
            await message.answer(text=f"При изменении ссылки произошла ошибка."
                                      f" Обратитесь в техподдежку",
                                 reply_markup=default_keyboard.as_markup())


# Редактирование теста

@dp.message(AdminState.access_change_test)
async def access_change_test(message: Message, state: FSMContext):
    if message.text == "Назад":
        text = "Вы перешли в админ панель"
        keyboard = admin_keyboard
        await state.set_state(AdminState.change)
        await bot.send_photo(chat_id=message.from_user.id,
                             photo=types.FSInputFile(path="images/admin.jpg"),
                             caption=text,
                             reply_markup=keyboard.as_markup(resize_keyboard=True))
    elif message.text == "Удалить старый тест":
        if truncate_old_test(conn, admin_tg_id):
            await state.set_state(AdminState.create_new_test_questions)
            await message.answer("Введите новый вопрос", reply_markup=ReplyKeyboardRemove())
        else:
            await message.answer("При удалении старого теста произошла ошибка.\n"
                                 "Пожалуйста обратитесь в тех поддержку")
    elif message.text == "Поменять картинки дизайна":
        directory = "C:/Users/admin/PycharmProjects/bot_nail/images/design"
        await message.answer("Текущие дизайны:")
        files = os.listdir(directory)
        for image in files:
            await bot.send_photo(chat_id=message.from_user.id,
                                 photo=types.FSInputFile(path=f"images/design/{image}"),
                                 reply_markup=create_change_design_keyboard(image).as_markup())


@dp.message(AdminState.create_new_test_questions)
async def create_new_test_questions(message: Message, state: FSMContext):
    if len(message.text) == 0:
        text = "Пожалуйста введите корректный вопрос"
        await message.answer(text, reply_markup=ReplyKeyboardRemove())
    else:
        await state.update_data(question=message.text)
        await message.answer("Вы успешно создали первый вопрос")
        await state.set_state(AdminState.create_new_test_answer)
        text = "Теперь добавим 4 варианта ответа к вопросу:\nВведите первый вариант ответа"
        await message.answer(text, reply_markup=ReplyKeyboardRemove())
        await state.update_data(answers=[])


@dp.message(AdminState.create_new_test_answer)
async def create_new_test_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    variant_answer = data.get("answers")
    if len(message.text) == 0:
        text = "Пожалуйста введите корректный вариант ответа"
        await message.answer(text, reply_markup=ReplyKeyboardRemove())
    else:

        variant_answer.append(message.text)
        await state.update_data(answers=variant_answer)

        if len(variant_answer) == 4:
            if create_questions_with_answers(conn, data.get("question"), variant_answer, admin_tg_id):
                await state.set_state(AdminState.create_new_question_or_not)
                await message.answer("Вы успешно создали вопрос!\nДобавить ещё вопрос?",
                                     reply_markup=answer_create_new_question_keyboard.as_markup(resize_keyboard=True))
            else:
                await message.answer("При создании вопроса произошла ошибка!.\n"
                                     "Пожалуйста обратитесь в тех поддержку")
                text = "Вы перешли в админ панель"
                keyboard = admin_keyboard
                await state.set_state(AdminState.change)
                await bot.send_photo(chat_id=message.from_user.id,
                                     photo=types.FSInputFile(path="images/admin.jpg"),
                                     caption=text,
                                     reply_markup=keyboard.as_markup(resize_keyboard=True))
        else:
            await message.answer("Вы успешно добавили ответ")
            text = f"Осталось ещё {4 - len(variant_answer)} варианта ответа к вопросу:"
            await message.answer(text, reply_markup=ReplyKeyboardRemove())


@dp.message(AdminState.create_new_question_or_not)
async def create_new_question_or_not(message: Message, state: FSMContext):
    if message.text == "Вернуться в админ панель":
        text = "Вы перешли в админ панель"
        keyboard = admin_keyboard
        await state.set_state(AdminState.change)
        await bot.send_photo(chat_id=message.from_user.id,
                             photo=types.FSInputFile(path="images/admin.jpg"),
                             caption=text,
                             reply_markup=keyboard.as_markup(resize_keyboard=True))
    elif message.text == "Добавить вопрос":
        await state.set_state(AdminState.create_new_test_questions)
        await message.answer("Введите новый вопрос", reply_markup=ReplyKeyboardRemove())

if __name__ == "__main__":
    asyncio.run(start())
