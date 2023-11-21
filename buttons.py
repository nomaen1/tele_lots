from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove

reg_button = [
    InlineKeyboardButton("Зарегистрироваться", callback_data="зарегаться"),
]
reg_keyboard = InlineKeyboardMarkup(one_time_keyboard=True,resize_keyboard=True).add(*reg_button)

agree_button = [
    InlineKeyboardButton("Ознакомлен", callback_data="ознакомлен"),
]
agree_keyboard = InlineKeyboardMarkup(one_time_keyboard=True,resize_keyboard=True).add(*agree_button)

# take_buttons = [
#     InlineKeyboardButton("Беру", callback_data="беру"),
# ]
# take_keyboard = InlineKeyboardMarkup(one_time_keyboard=True,resize_keyboard=True).add(*take_buttons)

got_button = [
    InlineKeyboardButton("Ознакомлен", callback_data="ознакомлен")
]
got_keyboard = InlineKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True).add(*got_button)

