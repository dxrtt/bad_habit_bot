import asyncio
import aioschedule
import logging
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from aiogram.utils.markdown import text, bold, italic, code, pre
from aiogram.types import ParseMode, ChatActions

import keyboards
from sqlihter import SQLighter

API_TOKEN = ''

logging.basicConfig(level=logging.INFO)

storage = MemoryStorage()

# init
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)
db = SQLighter('habitdb.db')


# Классы состояний
class HabitAdd(StatesGroup):
    name = State()


class HabitWatch(StatesGroup):
    HabitList = State()
    HabitEdit = State()
    HabitBreak = State()


class Testform(StatesGroup):
    name = State()


# Handlers

# Приветствие пользователя
@dp.message_handler(commands=['start'], state='*')
async def send_welcome(message: types.Message):
    await message.reply("Привет!\nЯ бот для борьбы с вредными привычками.\nЧто будем делать?\n/help - помощь",
                        reply_markup=keyboards.inline_hello_kb)
    db.achievements_add_user(message.from_user.id)


# Добавление привычки - первый этап
@dp.callback_query_handler(lambda c: c.data == 'add')
async def process_callback_button1(callback_query: types.CallbackQuery, state: FSMContext):
    # await bot.answer_callback_query(callback_query.id)
    await bot.answer_callback_query(callback_query.id, text='Напишите название привычки', show_alert=True)
    # await bot.send_message(callback_query.from_user.id, 'Добавляем привычку')
    await HabitAdd.name.set()
    await bot.send_message(callback_query.from_user.id, 'Напишите название привычки')


# Добавление привычки - ввод названия привычки
@dp.message_handler(state=HabitAdd.name)
async def habitname(message: types.Message, state: FSMContext):
    # Проверка длины названия привычки
    if len(message.text) > 30:
        await bot.send_message(message.chat.id, 'Слишком длинное название, попробуйте ввести более короткое название')
    else:
        # Отправляем привычку в БД
        db.add_habit(message.from_user.id, message.text, datetime.today().strftime("%d/%m/%Y %H:%M:%S"))
        await bot.send_message(message.chat.id, 'Привычка добавлена')
        await bot.send_message(message.from_user.id, 'Что делаем дальше?', reply_markup=keyboards.inline_hello_kb)
        await state.finish()


# Просмотр привычки
@dp.callback_query_handler(lambda c: c.data == 'watch')
async def process_callback_button1(callback_query: types.CallbackQuery):
    # Получаем массив привычек и формируем клавиатуру
    kb_array = db.watch_habit(str(callback_query.from_user.id))
    testwatch_kb = InlineKeyboardMarkup()
    for i in range(len(kb_array)):
        testwatch_kb.add(InlineKeyboardButton(kb_array[i][0], callback_data=kb_array[i][0]))
    testwatch_kb.add(keyboards.inline_button_menu)

    await bot.send_message(callback_query.from_user.id, text='Вот список ваших привычек:', reply_markup=testwatch_kb)
    await HabitWatch.HabitList.set()


# Просмотр достижений
@dp.callback_query_handler(lambda c: c.data == 'achievements')
async def habit_achievments(callback_query: types.CallbackQuery):
    achievements = db.achievements_user(callback_query.from_user.id)
    message = "Ваши достижения:\n\n"

    if achievements[0][0]:
        message += "Продержаться 1 день без любой привычки: 🟢\n"
    else:
        message += "Продержаться 1 день без любой привычки: 🔴\n"

    if achievements[0][1]:
        message += "Продержаться 7 дней без любой привычки: 🟢\n"
    else:
        message += "Продержаться 7 дней без любой привычки: 🔴\n"

    message += "\nГлавное меню:"

    await bot.send_message(callback_query.from_user.id, message, reply_markup=keyboards.inline_hello_kb)


# Переход в главное меню
@dp.callback_query_handler(lambda c: c.data == 'menu')
async def goto_menu(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.send_message(callback_query.from_user.id, 'Что будем делать?', reply_markup=keyboards.inline_hello_kb)


# Переход в главное меню
@dp.callback_query_handler(lambda c: c.data == 'menu', state=HabitWatch.HabitEdit)
async def goto_menu(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.send_message(callback_query.from_user.id, 'Что будем делать?', reply_markup=keyboards.inline_hello_kb)
    await state.finish()


# Помощь
@dp.message_handler(commands=['help'])
async def cmd_start(message: types.Message, state: FSMContext):
    # await Testform.name.set()
    await bot.send_message(message.from_user.id, "https://telegra.ph/Instrukciya-po-ispolzovaniyu-bota-01-10")
    # await message.reply('Pishi your name')


# Меню привычки - вывод информации и действия с ней
@dp.callback_query_handler(lambda c: c.data, state=HabitWatch.HabitList)
async def habit_watch(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'menu':
        await bot.send_message(callback_query.from_user.id, 'Возвращаемся в меню',
                               reply_markup=keyboards.inline_hello_kb)
        await state.finish()

    # Получаем информацию о привычке из БД и форматируем
    habit_info = db.habit_info(callback_query.from_user.id, callback_query.data)
    habit_status = db.habit_notifications_getstatus(habit_info[0][2])
    date_time_obj = datetime.strptime(habit_info[0][3], '%d/%m/%Y %H:%M:%S')
    deltatime = datetime.today() - date_time_obj
    notif_deltatime = datetime.today() - datetime.strptime(habit_info[0][1], '%d/%m/%Y %H:%M:%S')

    habit_message = '📌 ' + text(bold('Привычка: ')) + habit_info[0][0] + '\n' + text(bold('📅 Дата начала: ')) + str(
        habit_info[0][1]) + \
                    '\n\n' + text(bold('⏳ Времени прошло: ')) + '\nДней: ' + str(deltatime.days) + '\nЧасов: ' + \
                    str(int(deltatime.seconds / 3600)) + '\nМинут: ' + str(int((deltatime.seconds / 60) % 60)) + \
                    '\nСекунд: ' + str(int((deltatime.seconds) % 60)) + '\n\n' + text(bold('📉 Последние срывы: ')) \
                    + '\nДата последнего срыва: ' + str(habit_info[0][3]) + '\nВсего срывов: ' + str(habit_info[0][5]) \
                    + '\nПричина последнего срыва: ' + str(habit_info[0][4])

    if habit_status[0][0]:
        habit_message += '\n\n🛎 Уведомления включены'
    else:
        habit_message += '\n\n🛎 Уведомления отключены'

    habit_message += '\n\nВыберите действие:'

    await bot.send_message(callback_query.from_user.id, habit_message, reply_markup=keyboards.inline_habit_kb,
                           parse_mode=ParseMode.MARKDOWN_V2)

    # Мотивация
    if (notif_deltatime.days > 1) & (habit_info[0][5] == 0):
        msg = text(" 🎉 ", code("Ты продержался уже больше дня, так держать!"), " 🎉 ")
        await bot.send_message(callback_query.from_user.id, msg, parse_mode=ParseMode.MARKDOWN_V2)
    elif habit_info[0][5] > 0:
        msg = text(code('― Побороть дурные привычки легче сегодня, чем завтра. ~ Конфуций'))
        await bot.send_message(callback_query.from_user.id, msg, parse_mode=ParseMode.MARKDOWN_V2)

    await state.update_data(habit_id=(habit_info[0][2]))
    await HabitWatch.HabitEdit.set()


# Удаление привычки
@dp.callback_query_handler(lambda c: c.data == 'del', state=HabitWatch.HabitEdit)
async def habit_del(callback_query: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    db.delete_habit(user_data['habit_id'])
    await bot.send_message(callback_query.from_user.id, f"Привычка удалена", reply_markup=keyboards.inline_hello_kb)
    await state.finish()


# Регистрация срыва привычки
@dp.callback_query_handler(lambda c: c.data == 'break', state=HabitWatch.HabitEdit)
async def habit_break(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.send_message(callback_query.from_user.id, 'Укажите причину срыва')
    await HabitWatch.HabitBreak.set()


# Регистрация срыва привычки - ввод причины
@dp.message_handler(state=HabitWatch.HabitBreak)
async def habit_break_reason(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    db.update_habit_date(user_data['habit_id'], datetime.today().strftime("%d/%m/%Y %H:%M:%S"), message.text)
    await bot.send_message(message.from_user.id, 'Счетчик времени обновлен',
                           reply_markup=keyboards.inline_hello_kb)
    await state.finish()


# Включение/отключение уведомлений
@dp.callback_query_handler(lambda c: c.data == 'notifications', state=HabitWatch.HabitEdit)
async def habit_notifications(callback_query: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    status = db.habit_notifications_getstatus(user_data['habit_id'])
    if status[0][0]:
        db.habit_notifications_setstatus(user_data['habit_id'], False)
        await bot.send_message(callback_query.from_user.id, 'Уведомления отключены')
        await bot.send_message(callback_query.from_user.id, 'Главное меню', reply_markup=keyboards.inline_hello_kb)
    else:
        db.habit_notifications_setstatus(user_data['habit_id'], True)
        await bot.send_message(callback_query.from_user.id, 'Уведомления включены')
        await bot.send_message(callback_query.from_user.id, 'Главное меню', reply_markup=keyboards.inline_hello_kb)

    await state.finish()


# Отправляем уведомления
async def on_startup(x):
    asyncio.create_task(scheduled(600))


# Сами уведомления
async def scheduled(wait_for):
    while True:
        await asyncio.sleep(wait_for)

        habitslist = db.habit_notifications()
        for h in habitslist:
            if h[6]:
                date_time_obj = datetime.strptime(h[3], '%d/%m/%Y %H:%M:%S')
                deltatime = datetime.today() - date_time_obj

                if deltatime.days >= 1:
                    db.achievements_settrue(h[1], "one_day")

                if (deltatime.days >= 1) & (h[4] == False):
                    message = "Вы боритесь с привычкой '" + str(h[2]) + "' уже больше одного дня!\nПоздравляем!🎉"
                    await bot.send_message(h[1], message)
                    db.habit_notifications_settrue(h[0], "one_day_not")
                    print(h[2])

                if deltatime.days >= 7:
                    db.achievements_settrue(h[1], "seven_day")

                if (deltatime.days >= 7) & (h[5] == False):
                    message = "Вы боритесь с привычкой '" + str(h[2]) + "' уже больше 7 дней!\nВы молодец!🎉"
                    await bot.send_message(h[1], message)
                    db.habit_notifications_settrue(h[0], "sevn_day_not")
                    print(h[2])


if __name__ == '__main__':
    # executor.start_polling(dp, skip_updates=True)
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)  # вкл напоминания
    # executor.start(dp, scheduled(10))
