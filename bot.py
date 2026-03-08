import telebot

TOKEN =8663322759:AAH3H8m-fk95x4CqcOyofmtL9KVyrR8ny5Q
import logging
import sqlite3
import datetime

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "PASTE_YOUR_TOKEN"
OWNER_ID = 2123569990
SUPPORT = "@gyujnb"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

conn = sqlite3.connect("nutrition_bot.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY,
paid INTEGER DEFAULT 0,
premium INTEGER DEFAULT 0,
trial INTEGER DEFAULT 0,
trial_end TEXT,
water INTEGER DEFAULT 0,
steps INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks(
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
text TEXT,
done INTEGER DEFAULT 0
)
""")

conn.commit()

menu = ReplyKeyboardMarkup(resize_keyboard=True)
menu.add("📋 Задачи","🥗 Рецепты")
menu.add("💧 Вода","🚶 Шаги")
menu.add("🎯 Цель","🛒 Продукты")
menu.add("👑 Подписка","🆘 Поддержка")

recipes_basic = [
"Омлет с овощами",
"Куриная грудка с салатом",
"Рыба с рисом",
"Творог с фруктами"
]

recipes_premium = [
"Лосось с авокадо",
"Креветки с киноа",
"ПП паста с курицей",
"Боул с тунцом",
"Овсяноблин с бананом"
]

products = [
"куриная грудка",
"яйца",
"рис",
"гречка",
"овощи",
"творог",
"овсянка",
"рыба"
]

def check_access(user_id):

    cursor.execute("SELECT paid,trial,trial_end FROM users WHERE id=?",(user_id,))
    user = cursor.fetchone()

    if not user:
        return False

    if user[0] == 1:
        return True

    if user[1] == 1:
        end = datetime.datetime.fromisoformat(user[2])
        if datetime.datetime.now() < end:
            return True

    return False


@dp.message_handler(commands=["start"])
async def start(message: types.Message):

    cursor.execute(
        "INSERT OR IGNORE INTO users(id) VALUES(?)",
        (message.from_user.id,)
    )
    conn.commit()

    await message.answer(
        "🥗 Бот правильного питания\n\n"
        "Помогаю:\n"
        "• похудеть\n"
        "• набрать массу\n"
        "• контролировать питание\n"
        "• следить за водой и шагами",
        reply_markup=menu
    )

    await bot.send_message(
        OWNER_ID,
        f"Новый пользователь: {message.from_user.id}"
    )


@dp.message_handler(lambda m: m.text=="🆘 Поддержка")
async def support(message: types.Message):

    await message.answer(
        f"Если возникли проблемы\n"
        f"Напишите: {SUPPORT}"
    )


@dp.message_handler(lambda m: m.text=="📋 Задачи")
async def tasks(message: types.Message):

    cursor.execute(
        "SELECT id,text,done FROM tasks WHERE user_id=?",
        (message.from_user.id,)
    )

    rows = cursor.fetchall()

    text="Ваши задачи:\n\n"

    for r in rows:

        if r[2]==1:
            text+=f"✅ {r[1]}\n"
        else:
            text+=f"❌ {r[1]} (/done {r[0]})\n"

    await message.answer(text)


@dp.message_handler(commands=["task"])
async def add_task(message: types.Message):

    text = message.text.replace("/task ","")

    cursor.execute(
        "INSERT INTO tasks(user_id,text) VALUES(?,?)",
        (message.from_user.id,text)
    )

    conn.commit()

    await message.answer("Задача добавлена")


@dp.message_handler(commands=["done"])
async def done(message: types.Message):

    task_id = message.text.split()[1]

    cursor.execute(
        "UPDATE tasks SET done=1 WHERE id=?",
        (task_id,)
    )

    conn.commit()

    await message.answer("Задача выполнена")


@dp.message_handler(lambda m: m.text=="🥗 Рецепты")
async def recipes(message: types.Message):

    cursor.execute(
        "SELECT premium FROM users WHERE id=?",
        (message.from_user.id,)
    )

    user = cursor.fetchone()

    text="Рецепты ПП:\n\n"

    for r in recipes_basic:
        text+=f"• {r}\n"

    if user and user[0]==1:

        text+="\n👑 Premium рецепты:\n"

        for r in recipes_premium:
            text+=f"• {r}\n"

    await message.answer(text)


@dp.message_handler(lambda m: m.text=="💧 Вода")
async def water(message: types.Message):

    cursor.execute(
        "UPDATE users SET water=water+1 WHERE id=?",
        (message.from_user.id,)
    )

    conn.commit()

    await message.answer(
        "💧 Стакан воды записан\n"
        "Норма 8-10 стаканов"
    )


@dp.message_handler(lambda m: m.text=="🚶 Шаги")
async def steps(message: types.Message):

    await message.answer(
        "Введите сколько шагов прошли сегодня"
    )


@dp.message_handler(lambda m: m.text.isdigit())
async def save_steps(message: types.Message):

    steps = int(message.text)

    cursor.execute(
        "UPDATE users SET steps=? WHERE id=?",
        (steps,message.from_user.id)
    )

    conn.commit()

    if steps >= 10000:

        await message.answer(
            "🔥 Отлично! Цель 10000 шагов выполнена"
        )

    else:

        await message.answer(
            "Попробуйте дойти до 10000 шагов"
        )


@dp.message_handler(lambda m: m.text=="🎯 Цель")
async def goal(message: types.Message):

    await message.answer(
        "Введите ваш вес и рост\n"
        "пример: 80 175"
    )


@dp.message_handler(lambda m: len(m.text.split())==2)
async def calc(message: types.Message):

    try:

        weight,height = map(int,message.text.split())

        ideal = height - 100

        diff = weight - ideal

        if diff > 0:

            months = round(diff/3)

            await message.answer(
                f"Идеальный вес ~ {ideal} кг\n"
                f"Похудение займёт примерно {months} месяцев"
            )

        else:

            await message.answer(
                "Ваш вес уже близок к идеальному"
            )

    except:
        pass


@dp.message_handler(lambda m: m.text=="🛒 Продукты")
async def products_list(message: types.Message):

    await message.answer(
        "Введите бюджет на продукты"
    )


@dp.message_handler(lambda m: m.text.isdigit())
async def budget(message: types.Message):

    money = int(message.text)

    text=f"🛒 Продукты на {money}₽:\n\n"

    for p in products:
        text+=f"• {p}\n"

    await message.answer(text)


@dp.message_handler(lambda m: m.text=="👑 Подписка")
async def sub(message: types.Message):

    kb = InlineKeyboardMarkup()

    kb.add(
        InlineKeyboardButton(
            "🎁 Пробный доступ 3 дня",
            callback_data="trial"
        )
    )

    kb.add(
        InlineKeyboardButton(
            "👑 Premium подписка",
            callback_data="premium"
        )
    )

    await message.answer(
        "Выберите подписку",
        reply_markup=kb
    )


@dp.callback_query_handler(lambda c: c.data=="trial")
async def trial(call: types.CallbackQuery):

    end = datetime.datetime.now()+datetime.timedelta(days=3)

    cursor.execute(
        "UPDATE users SET trial=1,trial_end=? WHERE id=?",
        (str(end),call.from_user.id)
    )

    conn.commit()

    await call.message.answer(
        "🎁 Пробный доступ активирован на 3 дня"
    )


@dp.callback_query_handler(lambda c: c.data=="premium")
async def premium(call: types.CallbackQuery):

    await call.message.answer(
        "👑 Premium подписка\n\n"
        "• больше рецептов\n"
        "• советы владельца\n"
        "• персональный план\n\n"
        f"Напишите для оплаты {SUPPORT}"
    )


@dp.message_handler(commands=["ask"])
async def ask(message: types.Message):

    cursor.execute(
        "SELECT premium FROM users WHERE id=?",
        (message.from_user.id,)
    )

    user = cursor.fetchone()

    if user and user[0]==1:

        await bot.send_message(
            OWNER_ID,
            f"Вопрос от {message.from_user.id}\n\n{message.text}"
        )

        await message.answer("Вопрос отправлен владельцу")

    else:

        await message.answer(
            "Функция доступна только Premium"
        )


@dp.message_handler()
async def forward(message: types.Message):

    if message.from_user.id != OWNER_ID:

        await bot.send_message(
            OWNER_ID,
            f"Сообщение от {message.from_user.id}:\n{message.text}"
        )


if __name__ == "__main__":
    executor.start_polling(dp)

