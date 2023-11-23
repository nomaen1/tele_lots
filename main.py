from aiogram import Dispatcher, Bot, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from state import RegistrationStates
from aiogram.utils.exceptions import MessageNotModified
from dotenv import load_dotenv
from buttons import *
from database import cursor
import logging, os, aioschedule, asyncio, time

load_dotenv('.env')

bot = Bot(token=os.environ.get('token2'))
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
logging.basicConfig(level=logging.INFO)

initial_amount = 400
previous_button_ids = {}
round_counter = 1
auction_counter = 1
first_click_user_id = None
user_clicks = {}

@dp.callback_query_handler(lambda call: call)
async def inline(call):
    global initial_amount, first_click_user_id
    user_id = call.from_user.id
    if call.data == "зарегаться":
        await register(call.message)
    elif call.data == "ознакомлен":
        cursor.execute(f"UPDATE users SET agreement = ? WHERE user_id = ?", (time.ctime(), call.from_user.id))
        cursor.connection.commit()
        await bot.send_message(call.message.chat.id, "Отлично👍 Теперь зарегистрируйтесь", reply_markup=reg_keyboard)
    elif call.data == "беру":
        if user_clicks.get(user_id, 0) < 2:
            # Увеличиваем счетчик нажатий
            user_clicks[user_id] = user_clicks.get(user_id, 0) + 1

            if first_click_user_id is None:
                first_click_user_id = user_id
                await process_callback_button(call)
                initial_amount = max(initial_amount + 50, 0)
                await send_winner(user_id, initial_amount)
                initial_amount = 400  # Сбросить initial_amount после отправки победителя

            elif first_click_user_id == user_id:
                # Пользователь нажимает второй раз
                await process_callback_button(call)
                initial_amount = max(initial_amount + 50, 0)
                await send_winner(user_id, initial_amount)
                initial_amount = 400  # Сбросить initial_amount после отправки победителя
            else:
                # Пользователь пытается нажать кнопку после того, как кто-то уже выиграл
                await call.answer("Кнопка уже была нажата другим пользователем.", show_alert=True)
        else:
            # Пользователь пытается нажать в третий раз
            await call.answer("Вы уже использовали свои две попытки.", show_alert=True)
        # if user_id not in user_clicks:
        #     user_clicks[user_id] = 0
        # if user_clicks[user_id] < 2:
        #     user_clicks[user_id] += 1
        #     if first_click_user_id is None:
        #         first_click_user_id = call.from_user.id
        #         await process_callback_button(call)
        #         global initial_amount
        #         initial_amount = max(initial_amount + 50, 0)
        #         await send_winner(call.from_user.id, initial_amount)
        #     initial_amount = 400

async def process_callback_button(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    try:
        await bot.edit_message_reply_markup(chat_id=callback_query.message.chat.id,
                                            message_id=callback_query.message.message_id,
                                            reply_markup=None)
    except MessageNotModified:
        pass

def reset_registration():
    global first_click_user_id
    first_click_user_id = None

@dp.message_handler(commands='start')
async def start(message:types.Message):
    cursor.execute(f"SELECT * FROM users WHERE user_id = '{message.from_user.id}';")
    result = cursor.fetchall()
    if result == []:
        cursor.execute(f"""INSERT INTO users (user_id, username) VALUES ('{message.from_user.id}', '{message.from_user.username}');""")
    cursor.connection.commit()
    await message.answer("""Правила голландоского аукциона "Турецкие авиалинии - Сентябрь 2023"                                                                                                
1        👨🏻‍💻 Аукциона автоматический.                                                                                        
2        🥇 Первый написавший в определенный промежуток времени, выигрывает лот со стоимостью соответствующий этому времени. Фиксируется время сообщения.                                                                                        
3        ⛔ Человек отказавшийся от лота в течение  3 часов после выигрыша, вноситься в бан на участие в Голландском аукционе "Турецкие авиалинии - Сентябрь 2023", его лот перевыставляется повторно на аукционе. Отказавший от лота больше 3 часов после выигрыша вноситься в бан на участие на Голландских аукционах на полгода.                                                                                        
4        🔁 Выигранный лот разрешается перепродать или подарить только ВП компанний.                                                                                        
5        ⚠️ 1 сотрудник может купить только 1 лот  на данном ауцкионе.\n

Условия по выигранным лотам на Голландском аукционе "Турецкие авиалинии - Сентябрь 2023"                                                                                                
1        📆 Срок выписки билетов до 31 декабря 2023.                                                                                        
2        📅 Даты путешествия до 01 сентября 2024 года                                                                                        
3        🧑🏻‍✈️ Маршрут  - в любой город Турций 🇹🇷 (туда и обратно) с 1 остановкой Стамбуле или прямой рейс в пункт назначения  и  возврат в Бишкек. Разрешается прилет в 1 город, вылет из другого.                                                                                        
4        🗺 По подбору маршрута можете подобрать рейсы у агентов или в интернете, потом отправить данный маршрут на почту air.manager@concept.kg 📧 для проверки наличия мест. После подтверждения, данный маршрут бронируется на данные пассажира, и выкупается в течение 2 дней.                                                                                        
5        🔃 Таксы включены в стоимость лота. Расчет в сомах на день выписки по коммерческому курсу компании.                                                                                        
6        ❗ ❗ ❗ На выигранные лоты не распространяется оплата в рассрочку. Разрешается оплата через стандартный займ у компании и оплата сразу. В виде исключения разрешается оплатить полную стоимость с первого получения вознаграждения.""", reply_markup=agree_keyboard)

async def register(message:types.Message):
    await message.answer("Введите ваше имя")
    await RegistrationStates.name.set()

@dp.message_handler(state=RegistrationStates.name)
async def process_name(message: types.Message, state: FSMContext):
    name = message.text
    cursor.execute("UPDATE users SET name = ? WHERE user_id = ?", (name, message.from_user.id))
    cursor.connection.commit()
    await state.update_data(name=name)
    await message.reply("Теперь введите вашу фамилию:")
    await RegistrationStates.lastname.set()

@dp.message_handler(state=RegistrationStates.lastname)
async def process_surname(message: types.Message, state: FSMContext):
    lastname = message.text
    cursor.execute("UPDATE users SET lastname = ? WHERE user_id = ?", (lastname, message.from_user.id))
    cursor.connection.commit()
    await state.update_data(lastname=lastname)
    user_data = await state.get_data()
    await state.finish()
    await message.reply(f"Спасибо за регистрацию, {user_data['name']} {user_data['lastname']}!")
    await message.answer("⏳Мы вам сообщим когда аукцион начнется. 📧Ожидайте сообщение от меня")



async def send_auction_start_message():
    global initial_amount, previous_button_ids, auction_counter, round_counter

    cursor.execute("SELECT user_id, agreement, name, lastname FROM users")
    users = cursor.fetchall()


    if initial_amount == 400:
        for user_id, agreement, name, lastname in users:
            if is_user_eligible(user_id, agreement, name, lastname):
                message_text = f"👨‍⚖ Аукцион начался - Лот {round_counter} -  начальная цена 💲{initial_amount}. Всем удачи!)"
                take_button = types.InlineKeyboardButton("Беру", callback_data="беру")
                take_keyboard = types.InlineKeyboardMarkup()
                take_keyboard.add(take_button)
                previous_button_id = previous_button_ids.get(user_id)
                if previous_button_id:
                    try:
                        await bot.edit_message_reply_markup(chat_id=user_id, message_id=previous_button_id, reply_markup=None)
                    except MessageNotModified:
                        pass
                sent_message = await bot.send_message(user_id, message_text, reply_markup=take_keyboard)
                previous_button_ids[user_id] = sent_message.message_id

        initial_amount = max(initial_amount - 50,0)

    elif 250 <= initial_amount < 400:
        for user_id, agreement, name, lastname in users:
            if is_user_eligible(user_id, agreement, name, lastname):
                message_text = f"👨‍⚖ Цена уменьшилась! - Лот {round_counter} -  начальная цена 💲{initial_amount}. Всем удачи!)"
                take_button = types.InlineKeyboardButton("Беру", callback_data="беру")
                take_keyboard = types.InlineKeyboardMarkup()
                take_keyboard.add(take_button)
                previous_button_id = previous_button_ids.get(user_id)
                if previous_button_id:
                    try:
                        await bot.edit_message_reply_markup(chat_id=user_id, message_id=previous_button_id, reply_markup=None)
                    except MessageNotModified:
                        pass
                sent_message = await bot.send_message(user_id, message_text, reply_markup=take_keyboard)
                previous_button_ids[user_id] = sent_message.message_id
                
        initial_amount = max(initial_amount - 50,0)


    elif initial_amount < 250:
        for user_id, agreement, name, lastname, in users:
            if is_user_eligible(user_id, agreement, name, lastname):
                message_text = f"😊 Аукцион {auction_counter} закончился."
                await bot.send_message(user_id, message_text)
                await stop_scheduler()
                initial_amount = 400

        auction_counter += 1
        round_counter += 1
        if auction_counter <= 10:
            await scheduler()
        else:
            for user_id, agreement, name, lastname, in users:
                if is_user_eligible(user_id, agreement, name, lastname):
                    await bot.send_message(user_id, "На сегодня аукцион закончился. Ждите следующего начала")
            await stop_scheduler()


    

async def send_winner(user_id, price):
    global auction_counter, initial_amount, round_counter
    cursor.execute(f"SELECT name, lastname, winner FROM users where user_id = {user_id}")
    buyer = cursor.fetchone()
    if buyer:
        name, lastname, winner = buyer
        # if winner < 2:
        winner = winner + 1
        cursor.execute(f"UPDATE users SET winner = ?, price = ? WHERE user_id = ?", (winner, price, user_id))
        cursor.connection.commit()
        cursor.execute(f"SELECT user_id FROM users")
        users = cursor.fetchall()
        for user in users:
            user = user[0]
            message_text = f"👨‍⚖ У нас есть победитель! Пользователь {name} {lastname} выиграл - Лот {round_counter}  - за 💲{initial_amount}."
            await bot.send_message(user, message_text)
            message_text2 = f"😊 Аукцион {auction_counter} закончился."
            await bot.send_message(user, message_text2)
        auction_counter += 1
        if auction_counter == 11:
            await bot.send_message(user_id, "На сегодня аукцион закончился. Ждите следующего начала")
            await stop_scheduler()
        round_counter += 1
        reset_registration()

        # elif winner == 2:
            
        #     message_text = f"👨‍⚖ Вы больше не можете участвовать в аукционах."
        #     await bot.send_message(user_id, message_text)
        #     initial_amount = max(initial_amount - 50, 0)



def is_user_eligible(user_id, agreement, name, lastname):
    return agreement is not None and agreement != 0 and name is not None and lastname is not None

async def scheduler():
    aioschedule.every(15).seconds.do(send_auction_start_message)

    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)

async def stop_scheduler():
    aioschedule.clear()
    print("Scheduler stopped")

async def on_startup(_):
    asyncio.create_task(scheduler())

executor.start_polling(dp, skip_updates=True, on_startup=on_startup)