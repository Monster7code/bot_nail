from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from request_db import *
from main import get_conn

# Поскольку бот для всех уникальный мы должны явно указать id админа
admin_tg_id = "6259845330"


default_keyboard = ReplyKeyboardBuilder()
default_keyboard.row(types.KeyboardButton(text="Назад"))


sing_up = InlineKeyboardBuilder()
sing_up.add(types.InlineKeyboardButton(text="Записаться", callback_data="sign_up"))


def create_start_keyboard():
    start_keyboard = InlineKeyboardBuilder()
    start_keyboard.add(types.InlineKeyboardButton(text="📅 Записаться на услуги", callback_data="sign_up_service"),
                               types.InlineKeyboardButton(text="💅 Подобрать дизайн", callback_data="choice_design"))

    start_keyboard.row(types.InlineKeyboardButton(text="🌈 Палитра цветов", callback_data="palette_colors"),
                               types.InlineKeyboardButton(text="🔎 Информация об услугах", callback_data="info_service"))

    start_keyboard.row(types.InlineKeyboardButton(text="ℹ️ Актуальная информация", callback_data="info"))

    start_keyboard.row(types.InlineKeyboardButton(text="Инстаграм",
                                                          url=f"{get_social_link(get_conn(),
                                                                             "инстаграм", admin_tg_id)}"),
                               types.InlineKeyboardButton(text="Вконтакте",
                                                          url=f"{get_social_link(get_conn(),
                                                                             "вконтакте", admin_tg_id)}"))
    return start_keyboard


choice_design = InlineKeyboardBuilder()


def generate_keyboard(list_answer):
    answer_keyboard = InlineKeyboardBuilder()
    answer_keyboard.row(types.InlineKeyboardButton(text=list_answer[0], callback_data="first_answer"),
                       types.InlineKeyboardButton(text=list_answer[1], callback_data="second_answer"))

    answer_keyboard.row(types.InlineKeyboardButton(text=list_answer[2], callback_data="third_answer"),
                       types.InlineKeyboardButton(text=list_answer[3], callback_data="fourth_answer"))
    return answer_keyboard


def generate_signup_keyboard(list_time):
    time_keyboard = InlineKeyboardBuilder()
    for time in list_time:
        time_keyboard.add(types.InlineKeyboardButton(text=f"{time}", callback_data="sign_up|"+str(time)))
    time_keyboard.row(types.InlineKeyboardButton(text="Назад", callback_data="back_time"))
    return time_keyboard


def create_service_keyboard(conn, user_id):
    service_keyboard = InlineKeyboardBuilder()
    for service in get_master_service(conn, user_id):
        service_keyboard.add((types.InlineKeyboardButton(text=f"{service[0]}", callback_data="choice_service|"+service[0])))

    service_keyboard.row(types.InlineKeyboardButton(text="Назад", callback_data="back_to_day"))
    return service_keyboard


'''
Админская часть
'''
admin_keyboard = ReplyKeyboardBuilder()
admin_keyboard.row(types.KeyboardButton(text="Назад"))
admin_keyboard.row(types.KeyboardButton(text="Поменять приветственное сообщение"))
admin_keyboard.row(types.KeyboardButton(text="Поменять информацию об услугах"))
admin_keyboard.row(types.KeyboardButton(text="Редактировать услуги"))
admin_keyboard.row(types.KeyboardButton(text="Редактировать палитру цветов"))
admin_keyboard.row(types.KeyboardButton(text="Редактировать актуальную информацию"))
admin_keyboard.row(types.KeyboardButton(text="Редактировать ссылки на социальные сети"))
admin_keyboard.row(types.KeyboardButton(text="Редактировать тест для выбора дизайна"))

keyboard_swap_main = ReplyKeyboardBuilder()
keyboard_swap_main.row(types.KeyboardButton(text="Поменять текст"), types.KeyboardButton(text="Поменять картинку"))
keyboard_swap_main.row(types.KeyboardButton(text="Назад"))


social_links_keyboard = ReplyKeyboardBuilder()
social_links_keyboard.row(types.KeyboardButton(text="Инстаграм"), types.KeyboardButton(text="Вконтакте"))
social_links_keyboard.row(types.KeyboardButton(text="Назад"))


def create_drop_service_keyboard(service):
    drop_service_keyboard = InlineKeyboardBuilder()
    drop_service_keyboard.add(types.InlineKeyboardButton(text=f"Удалить", callback_data="drop_service|" + service))
    return drop_service_keyboard


def create_drop_palette_keyboard(index):
    drop_palette_keyboard = InlineKeyboardBuilder()
    drop_palette_keyboard.add(types.InlineKeyboardButton(text=f"Удалить", callback_data="drop_image|" + index))
    return drop_palette_keyboard


# Редактирование теста
access_change_test_keyboard = ReplyKeyboardBuilder()
access_change_test_keyboard.row(types.KeyboardButton(text="Удалить старый тест"),
                       types.KeyboardButton(text="Поменять картинки дизайна"))
access_change_test_keyboard.row(types.KeyboardButton(text="Назад"))

answer_create_new_question_keyboard = ReplyKeyboardBuilder()

answer_create_new_question_keyboard.row(types.KeyboardButton(text="Добавить вопрос"))
answer_create_new_question_keyboard.row(types.KeyboardButton(text="Вернуться в админ панель"))


def create_change_design_keyboard(name_image):
    if name_image == "first.jpg":
        number_image = "первую"
    elif name_image == "second.jpg":
        number_image = "вторую"
    elif name_image == "third.jpg":
        number_image = "третью"
    elif name_image == "fourth.jpg":
        number_image = "четвертую"
    else:
        number_image = "Ошибка"
    change_design_keyboard = InlineKeyboardBuilder()
    change_design_keyboard.add(types.InlineKeyboardButton(text=f"Поменять {number_image} картинку",
                                                          callback_data="change_image|" + name_image))
    return change_design_keyboard
