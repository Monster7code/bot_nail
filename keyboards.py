from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder


sing_up = InlineKeyboardBuilder()
sing_up.add(types.InlineKeyboardButton(text="Записаться", callback_data="sign_up"))


start_keyboard = InlineKeyboardBuilder()
start_keyboard.add(types.InlineKeyboardButton(text="📅 Записаться на услуги", callback_data="sign_up_service"),
                           types.InlineKeyboardButton(text="💅 Подобрать дизайн", callback_data="choice_design"))

start_keyboard.row(types.InlineKeyboardButton(text="🌈 Палитра цветов", callback_data="palette_colors"),
                           types.InlineKeyboardButton(text="🔎 Информация об услугах", callback_data="info_service"))

start_keyboard.row(types.InlineKeyboardButton(text="ℹ️ Актуальная информация", callback_data="info"))

start_keyboard.row(types.InlineKeyboardButton(text="Инстаграм", url="https://www.instagram.com/"),
                   types.InlineKeyboardButton(text="Вконтакте", url="https://vk.com/"))

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
    return time_keyboard