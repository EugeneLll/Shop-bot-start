from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.callback_data import CallbackData
import sqlite3
import os.path
import phonecheck

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "Food.db")

carts_path = os.path.join(BASE_DIR, "carts.db")

goods = (
    "Карбонара",
    "4 Сезонахит",
    "Мюнхенская",
    "Болоньезе",
    "Чеддерони",
    "5 Сыров",
    "Митболло",
    "Спайси",
    "Кантри",
    "Барбекю",
    "Тоскана",
    "Чикен Карри",
    "Овощная",
    "Пепперони",
    "Мит&Чиз",
    "Говядина BURGER",
    "Ветчина и грибы",
    "Экстраваганzzа",
    "Митzzа",
    "Гипнотика",
    "Сытная",
    "Баварская",
    "Фермерская",
    "Прованс",
    "Пепперони Блюз",
    "Супер Пепперони",
    "Гавайская",
    "Маргарита",
    "Салями Ранч",
    "Охотничья",
)

payment_key = "284685063:TEST:MTY1Yzc1M2Y2NTAx"

API = "6232161036:AAEsvi3bXfbiTrkYzDl9S3XBcCZi9bfWiqM"

bot = Bot(token=API)
dp = Dispatcher(bot=bot, storage=MemoryStorage())

change = CallbackData("changing", "state_ord", "position", "size")


class Adress(StatesGroup):
    adr = State()
    menu_look = State()
    number = State()
    pay = State()


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button_1 = types.KeyboardButton(text="Меню")
    keyboard.add(button_1)
    await message.answer(
        f"Добро пожаловать в нашу доставку пиццы!", reply_markup=keyboard
    )


@dp.message_handler(lambda message: message.text == "Меню", state="*")
async def menu(message: types.Message, state: FSMContext):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)

    for i in goods:
        button = types.KeyboardButton(text=f"{i}")
        kb.add(button)
    b_1 = types.KeyboardButton(text="Корзина")
    kb.add(b_1)
    await Adress.menu_look.set()
    await message.answer(
        "Это наше меню на данный момент, нажмите на кнопку или введте название",
        reply_markup=kb,
    )


@dp.callback_query_handler(text="ord_med", state=Adress.menu_look)
async def medium(call: types.CallbackQuery):
    pizz = call.message.caption.split("\n")[0][:-1]
    sql = sqlite3.connect(carts_path)
    conn = sql.cursor()
    s = sqlite3.connect(db_path)
    c = s.cursor()
    conn.execute(
        f"CREATE TABLE IF NOT EXISTS ord{call.message.chat.id} (food TEXT, size TEXT, cost REAl)"
    )
    sql.commit()

    c.execute(f"SELECT med_price FROM menu WHERE name='{pizz}'")
    s.commit()
    pr = c.fetchone()
    conn.execute(
        f'INSERT INTO ord{call.message.chat.id} (food, size, cost) VALUES ("{pizz}", "средняя", {pr[0]})'
    )
    sql.commit()
    c.close()
    s.close()
    conn.close()
    sql.close()
    await call.message.answer(text=f"Средняя {pizz} добавлена в корзину")


@dp.callback_query_handler(text="ord_big", state=Adress.menu_look)
async def big(call: types.CallbackQuery):
    pizza = call.message.caption.split("\n")[0][:-1]
    sql = sqlite3.connect(carts_path)
    conn = sql.cursor()
    s = sqlite3.connect(db_path)
    c = s.cursor()
    conn.execute(
        f"CREATE TABLE IF NOT EXISTS ord{call.message.chat.id} (food TEXT, size TEXT, cost REAl)"
    )
    sql.commit()

    c.execute(f"SELECT big_price FROM menu WHERE name='{pizza}'")
    s.commit()
    pr = c.fetchone()
    conn.execute(
        f'INSERT INTO ord{call.message.chat.id} (food, size, cost) VALUES ("{pizza}", "большая", {pr[0]})'
    )
    sql.commit()
    c.close()
    s.close()
    conn.close()
    sql.close()
    await call.message.answer(text=f"Большая {pizza} добавлена в корзину")


@dp.message_handler(lambda message: message.text == "Корзина", state=Adress.menu_look)
async def cart(message: types.Message):
    pizza = {}
    buttons = []
    b_1 = types.KeyboardButton(text="Меню")
    buttons.append(b_1)
    summ = 0
    sql = sqlite3.connect(carts_path)
    conn = sql.cursor()
    conn.execute(f"SELECT * FROM ord{message.chat.id}")
    sql.commit()
    cart = conn.fetchall()
    conn.close()
    sql.close()
    if len(cart) > 0:
        for i in cart:
            if i[0] + ", " + i[1] not in pizza:
                pizza[i[0] + ", " + i[1]] = 1
            else:
                pizza[i[0] + ", " + i[1]] += 1
            summ += i[2]

        order = "Ваш заказ:\n"

        for i in pizza:
            order = order + i + " - x" + str(pizza[i]) + "\n"
        order += f"Общая цена заказа: {round(summ,2)}"
        b_2 = types.KeyboardButton(text="Оформить заказ")
        b_3 = types.KeyboardButton(text="Редактировать корзину")
        buttons.append(b_2)
        buttons.append(b_3)
    else:
        order = "Корзина пуста"
    kb = types.ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=True, row_width=2
    )

    kb.add(*buttons)
    await message.answer(order, reply_markup=kb)


@dp.message_handler(
    lambda message: message.text == "Оформить заказ", state=Adress.menu_look
)
async def order(message: types.Message):
    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True)
    button_1 = types.InlineKeyboardButton(
        text=f"Нет - Вернуться в корзину", callback_data="to_cart"
    )
    button_2 = types.InlineKeyboardButton(
        text=f"Да - ввести адрес", callback_data="adress"
    )
    keyboard.add(button_1)
    keyboard.add(button_2)
    await message.answer(
        "Вы действительно желаете оформить заказ?", reply_markup=keyboard
    )


@dp.message_handler(
    lambda message: message.text == "Редактировать корзину", state=Adress.menu_look
)
async def redact(message: types.Message):
    msg = ""
    pizza = {}
    sql = sqlite3.connect(carts_path)
    conn = sql.cursor()
    conn.execute(f"SELECT * FROM ord{message.chat.id}")
    sql.commit()
    cart = conn.fetchall()
    for i in cart:
        if i[0] + ", " + i[1] not in pizza:
            pizza[i[0] + ", " + i[1]] = 1
        else:
            pizza[i[0] + ", " + i[1]] += 1
    conn.close()
    sql.close()
    kb = types.InlineKeyboardMarkup(resize_keyboard=True, row_width=3)
    p_k = list(pizza.keys())
    for i in p_k:
        piz = i.split(", ")
        button = types.InlineKeyboardButton(
            text=f"❌{p_k.index(i)+1}",
            callback_data=change.new(
                state_ord="redact", position=f"{piz[0]}", size=f"{piz[1]}"
            ),
        )
        kb.add(button)
        msg = msg + f"{p_k.index(i)+1}. {i} x {pizza[i]}\n"
    kb.add(
        types.InlineKeyboardButton(text="Вернуться в карзину", callback_data="to_cart")
    )
    await message.answer(
        f"Нажмите на кнопку для удаления данной единицы товара\n{msg}", reply_markup=kb
    )


@dp.callback_query_handler(change.filter(), state=Adress.menu_look)
async def redact_ord(qery: types.CallbackQuery, callback_data: dict):
    pizza_chosen = [callback_data["position"], callback_data["size"]]
    pizza = {}

    msg = ""
    sql = sqlite3.connect(carts_path)
    conn = sql.cursor()
    conn.execute(
        f'DELETE FROM ord{qery.message.chat.id} WHERE food="{pizza_chosen[0]}" AND size="{pizza_chosen[1]}"'
    )
    sql.commit()
    conn.execute(f"SELECT * FROM ord{qery.message.chat.id}")
    sql.commit()
    cart = conn.fetchall()
    for i in cart:
        if i[0] + ", " + i[1] not in pizza:
            pizza[i[0] + ", " + i[1]] = 1
        else:
            pizza[i[0] + ", " + i[1]] += 1
    conn.close()
    sql.close()
    kb = types.InlineKeyboardMarkup(resize_keyboard=True, row_width=3)
    p_k = list(pizza.keys())
    for i in p_k:
        piz = i.split(", ")
        button = types.InlineKeyboardButton(
            text=f"❌{p_k.index(i)+1}",
            callback_data=change.new(
                state_ord="redact", position=f"{piz[0]}", size=f"{piz[1]}"
            ),
        )
        kb.add(button)
        msg = msg + f"{p_k.index(i)+1}. {i} x {pizza[i]}\n"
    kb.add(
        types.InlineKeyboardButton(text="Вернуться в карзину", callback_data="to_cart")
    )
    await qery.message.edit_text(
        f"Нажмите на кнопку для удаления данной единицы товара\n{msg}"
    )
    await qery.message.edit_reply_markup(reply_markup=kb)


@dp.callback_query_handler(text="to_cart", state=Adress.menu_look)
async def tocart(call: types.CallbackQuery):
    pizza = {}
    summ = 0
    buttons = []

    b_1 = types.KeyboardButton(text="Меню")
    buttons.append(b_1)
    sql = sqlite3.connect(carts_path)
    conn = sql.cursor()
    conn.execute(f"SELECT * FROM ord{call.message.chat.id}")
    sql.commit()
    cart = conn.fetchall()
    conn.close()
    sql.close()
    if len(cart) > 0:
        for i in cart:
            if i[0] + ", " + i[1] not in pizza:
                pizza[i[0] + ", " + i[1]] = 1
            else:
                pizza[i[0] + ", " + i[1]] += 1
            summ += i[2]

        order = "Ваш заказ:\n"
        for i in pizza:
            order = order + i + " - x" + str(pizza[i]) + "\n"
        order += f"Общая цена заказа: {round(summ,2)}"
        b_2 = types.KeyboardButton(text="Оформить заказ")
        b_3 = types.KeyboardButton(text="Редактировать корзину")
        buttons.append(b_2)
        buttons.append(b_3)
    else:
        order = "Корзина пуста"
    kb = types.ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=True, row_width=2
    )

    kb.add(*buttons)
    await call.message.answer(order, reply_markup=kb)


@dp.callback_query_handler(text="adress", state=Adress.menu_look)
async def adress(call: types.CallbackQuery, state: FSMContext):
    sql = sqlite3.connect(carts_path)
    conn = sql.cursor()
    conn.execute(f"SELECT adress FROM adresses WHERE id = {call.message.chat.id}")
    sql.commit()
    adr = conn.fetchone()
    if adr == None:
        await call.message.answer("Введите свой адрес")
    else:
        kb = types.InlineKeyboardMarkup(resize_keyboard=True)
        button_1 = types.InlineKeyboardButton(text=f"{adr[0]}", callback_data="confirm")
        await state.update_data(entered_adr=adr[0])
        kb.add(button_1)
        await call.message.answer("Введите свой адрес", reply_markup=kb)
    conn.close()
    sql.close()
    await Adress.adr.set()


@dp.message_handler(state=Adress.menu_look)
async def get_ord(message: types.Message, state: FSMContext):
    good = message.text.strip()
    if good in goods:
        s = sqlite3.connect(db_path)
        c = s.cursor()
        c.execute(
            f'SELECT name, ingredients, med_price, big_price, picture FROM menu WHERE name="{good}"'
        )

        records = c.fetchone()
        photo = open(records[4].strip('"'), "rb")
        keyboard = types.InlineKeyboardMarkup(resize_keyboard=True)
        button_1 = types.InlineKeyboardButton(
            text=f"Средняя 30 см - {round(records[2],2)}", callback_data="ord_med"
        )
        button_2 = types.InlineKeyboardButton(
            text=f"Боьшая 36 см - {round(records[3],2)}", callback_data="ord_big"
        )
        keyboard.add(button_1)
        keyboard.add(button_2)
        await message.answer_photo(
            photo, caption=f"{records[0]} \nСостав: {records[1]}", reply_markup=keyboard
        )
        photo.close()
    else:
        await message.answer(f"Введите заново или нажмите на кнопку")
        return


@dp.message_handler(state=Adress.adr)
async def get_adr(message: types.Message, state: FSMContext):
    adr = message.text
    await state.update_data(entered_adr=adr)
    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True, row_width=1)
    button_1 = types.InlineKeyboardButton(
        text=f"Да - Подтвердить адрес", callback_data="confirm"
    )
    button_2 = types.InlineKeyboardButton(
        text=f"Да - Подтвердить адрес и сохранить", callback_data="confirm_save"
    )
    button_3 = types.InlineKeyboardButton(
        text=f"Нет - Вернуться к вводу адреса", callback_data="adress"
    )
    keyboard.add(button_1)
    keyboard.add(button_2)
    keyboard.add(button_3)
    await message.answer("Это точно ваш адрес?", reply_markup=keyboard)


@dp.callback_query_handler(text="confirm", state=Adress.adr)
async def conf(call: types.CallbackQuery, state: FSMContext):
    await Adress.number.set()
    await call.message.answer(
        "Введите пожалуйста свой номер телефона в формате +375 XX XXXXXXX"
    )


@dp.callback_query_handler(text="confirm_save", state=Adress.adr)
async def conf(call: types.CallbackQuery, state: FSMContext):
    sql = sqlite3.connect(carts_path)
    conn = sql.cursor()

    adr = await state.get_data()
    conn.execute(
        f""" INSERT INTO adresses (id, adress)
  SELECT {call.message.chat.id}, "{adr["entered_adr"]}"  
    WHERE NOT EXISTS (SELECT * FROM adresses WHERE id = {call.message.chat.id});
    """
    )

    sql.commit()
    conn.execute(
        f"UPDATE adresses SET adress=\"{adr['entered_adr']}\" WHERE id = {call.message.chat.id}"
    )
    sql.commit()

    conn.close()
    sql.close()
    await Adress.number.set()
    await call.message.answer(
        "Введите пожалуйста свой номер телефона в формате +XXXXXXXXXXXX"
    )


@dp.message_handler(state=Adress.number)
async def get_num(message: types.Message, state: FSMContext):
    num = message.text

    if phonecheck.validate_phone_number(num):
        keyboard = types.InlineKeyboardMarkup(resize_keyboard=True, row_width=1)
        button_1 = types.InlineKeyboardButton(
            text=f"Да - Подтвердить номер телефона", callback_data="pay"
        )
        keyboard.add(button_1)
        await message.answer(
            "Нажмите на кнопку если вы уверены что это ваш номер и вы готовы перейти к оплате. В ином случае введите свой номер еще раз",
            reply_markup=keyboard,
        )
        await state.update_data(number=num)
    else:
        await message.answer("Номер введен не верно введите его еще раз")


@dp.callback_query_handler(text="pay", state=Adress.number)
async def conf(call: types.CallbackQuery, state: FSMContext):
    sql = sqlite3.connect(carts_path)
    conn = sql.cursor()
    conn.execute(f"SELECT cost FROM ord{call.message.chat.id}")
    sql.commit()
    order = conn.fetchall()
    price = sum(map(lambda x: x[0], order))
    conn.close()
    sql.close()
    await Adress.pay.set()
    await bot.send_invoice(
        call.message.chat.id,
        "Заказ пиццы",
        f"Заказ на сумму {round(price,2)} рублей",
        "invoice",
        payment_key,
        "USD",
        [types.LabeledPrice("Заказ пиццы", round(price * 100))],
    )


@dp.message_handler(text="confirmed", content_types=["text"], state=Adress.pay)
async def sucsess(message: types.Message, state: FSMContext):
    data = await state.get_data()
    adr = data["entered_adr"]
    num = data["number"]
    await state.finish()
    sql = sqlite3.connect(carts_path)
    conn = sql.cursor()
    s = sqlite3.connect(db_path)
    c = s.cursor()
    conn.execute(f"SELECT * FROM ord{message.chat.id}")
    sql.commit()
    order = conn.fetchall()
    conn.execute(f"DROP TABLE IF EXISTS ord{message.chat.id}")
    sql.commit()
    order_str = ", ".join(list(map(lambda x: x[0] + " " + x[1], order.copy())))
    price = sum(map(lambda x: x[2], order))
    print(order_str, price, adr, num)
    c.execute(
        """INSERT INTO confirmed (id, ord, price, adress, telephone) VALUES (?,?,?,?,?)""",
        (message.chat.id, order_str, price, adr, num),
    )
    s.commit()
    c.close()
    s.close()
    conn.close()
    sql.close()
    kb = types.ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=True, row_width=1
    )
    b_1 = types.KeyboardButton(text="Меню")
    kb.add(b_1)
    await message.answer("Заказ успешен ожидайте доставки", reply_markup=kb)


if __name__ == "__main__":
    executor.start_polling(dp)


""" 
types.ContentType.SUCCESSFUL_PAYMENT
1111 1111 1111 1026, 12/22, CVC 000.
DROP TABLE IF EXISTS table2

sql = sqlite3.connect(carts_path)
    conn = sql.cursor()
    s = sqlite3.connect(db_path)
    c = s.cursor()
    conn.execute(
    f"SELECT * FROM ord{message.chat.id}"
    )
    sql.commit()
    order=conn.fetchall()
    order_str=' '.join(list(map(lambda x: x[0] + " "+ x[1],order.copy())))
    price=sum(map(lambda x: x[2],order))
    c.execute(f"SELECT big_price FROM menu WHERE name=\'{pizza}\'")
    s.commit()
    pr=c.fetchone()
    conn.execute(f"INSERT INTO ord{call.message.chat.id} (food, size, cost) VALUES (\"{pizza}\", \"большая\", {pr[0]})")
    sql.commit()
    c.close()
    s.close()
    conn.close()
    sql.close()"""


# s = sqlite3.connect(db_path)
# c = s.cursor()
# c.execute("""SELECT name, ingredients, med_price, big_price FROM menu""")
"""records = c.fetchall()
    for pos in records:
        keyboard = types.InlineKeyboardMarkup(resize_keyboard=True)
        button_1 = types.InlineKeyboardButton(
            text=f"Средняя 30 см - {round(pos[2],2)}", callback_data="ord_med"
        )
        button_2 = types.InlineKeyboardButton(
            text=f"Боьшая 36 см - {round(pos[3],2)}", callback_data="ord_big"
        )
        keyboard.add(button_1)
        keyboard.add(button_2)
        await message.answer(f"{pos[0]} \nСостав: {pos[1]}", reply_markup=keyboard)"""
# c.close()
# s.close()


"""await bot.send_invoice(
    call.message.chat.id,
    "Заказ пиццы",
    f"Заказ на сумму {price} рублей",
    "invoice",
    payment_key,
    "USD",
    [types.LabeledPrice("Заказ пиццы", round(price * 100))],
)"""
