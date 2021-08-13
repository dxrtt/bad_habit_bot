from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, \
    InlineKeyboardButton

button_add = KeyboardButton('Добавить')
button_watch = KeyboardButton('Смотреть')
button_achievements = KeyboardButton('Достижения')

hello_kb = ReplyKeyboardMarkup()
hello_kb.add(button_add).add(button_watch).add(button_achievements)

# Общие кнопки
inline_button_menu = InlineKeyboardButton('Главное меню', callback_data='menu')
inline_button_back = InlineKeyboardButton('Назад', callback_data='back')

# Главное меню
inline_button_add = InlineKeyboardButton('📌 Добавить привычки', callback_data='add')
inline_button_watch = InlineKeyboardButton('📚 Смотреть привычки', callback_data='watch')
inline_button_achievements = InlineKeyboardButton('🏆 Смотреть достижения', callback_data='achievements')

inline_hello_kb = InlineKeyboardMarkup().add(inline_button_add).add(inline_button_watch).add(inline_button_achievements)

# Меню привычки
inline_button_break = InlineKeyboardButton('📉 Сорвался', callback_data='break')
inline_button_delete = InlineKeyboardButton('✂️Удалить', callback_data='del')
inline_button_notifies = InlineKeyboardButton('🛎 Включить/отключить уведомления', callback_data='notifications')

inline_habit_kb = InlineKeyboardMarkup().add(inline_button_break).add(inline_button_delete).add(inline_button_notifies).add(inline_button_menu)