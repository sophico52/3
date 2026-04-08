import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

TOKEN = "8585699588:AAH-7I3sS-iqKNmgYQ4MwweGAXOkTuQwT-A"

bot = Bot(token=TOKEN)
dp = Dispatcher()

user_scores = {}
user_results = {}
user_states = {}

# --- МЕНЮ ---
menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📘 Что это за специальность")],
        [KeyboardButton(text="💼 Где работать")],
        [KeyboardButton(text="🧠 Пройти тест")],
        [KeyboardButton(text="📚 Специальности колледжа")]
    ],
    resize_keyboard=True
)

menu_with_result = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📘 Что это за специальность")],
        [KeyboardButton(text="💼 Где работать")],
        [KeyboardButton(text="🧠 Пройти тест")],
        [KeyboardButton(text="📚 Специальности колледжа")],
        [KeyboardButton(text="📊 Мои результаты")]
    ],
    resize_keyboard=True
)

# --- ВОПРОСЫ ---
questions = [
    ("Ты нашел флешку. Что сделаешь?", [
        "Вставлю в комп",
        "Отнесу преподавателю",
        "Выброшу"
    ]),
    ("Пароль?", [
        "qwerty123",
        "Имя+дата",
        "Случайная фраза"
    ]),
]

correct_answers = {
    0: ("Отнесу преподавателю", 3),
    1: ("Случайная фраза", 3)
}

def get_result_text(score):
    if score <= 2:
        return "🫣 Не очень"
    elif score <= 4:
        return "👍 Норм"
    else:
        return "🔥 Отлично!"

# --- КАРТИНКИ ---
monkey = "https://cdn.pixabay.com/photo/2019/03/08/16/20/monkey-4042658_1280.jpg"

# --- СЕРТИФИКАТ ---
async def generate_certificate(name: str):
    url = "https://raw.githubusercontent.com/sophico52/3/main/cert_template.jpeg"

    response = requests.get(url)
    image = Image.open(BytesIO(response.content))

    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("arial.ttf", 80)
    except:
        font = ImageFont.load_default()

    width, height = image.size

    text_width = draw.textlength(name, font=font)

    x = (width - text_width) / 2
    y = height * 0.6  # чуть ниже центра — смотрится красиво

    draw.text((x, y), name, fill="black", font=font)

    output = BytesIO()
    image.save(output, format="JPEG")
    output.seek(0)

    return output

# --- СТАРТ ---
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привет 👋", reply_markup=menu)

# --- ТЕСТ С КАРТИНКОЙ ---
@dp.message(lambda m: m.text == "🧠 Пройти тест")
async def show_test(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🚀 Начать тест")],
            [KeyboardButton(text="В главное меню")]
        ],
        resize_keyboard=True
    )

    await message.answer_photo(
        photo=monkey,
        caption="🐒 Готов?\nЖми начать!",
        reply_markup=keyboard
    )

# --- НАЧАТЬ ТЕСТ ---
@dp.message(lambda m: m.text == "🚀 Начать тест")
async def start_test(message: types.Message):
    uid = message.from_user.id
    user_scores[uid] = 0
    user_states[uid] = {"stage": "test", "q": 0}

    await send_question(message.chat.id, uid)

async def send_question(chat_id, uid):
    q = user_states[uid]["q"]
    text, options = questions[q]

    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=o)] for o in options],
        resize_keyboard=True
    )

    await bot.send_message(chat_id, text, reply_markup=kb)

# --- ОТВЕТ ---
@dp.message(lambda m: user_states.get(m.from_user.id, {}).get("stage") == "test")
async def answer(message: types.Message):
    uid = message.from_user.id
    state = user_states[uid]

    q = state["q"]

    correct, points = correct_answers[q]
    if message.text == correct:
        user_scores[uid] += points

    state["q"] += 1

    if state["q"] < len(questions):
        await send_question(message.chat.id, uid)
    else:
        score = user_scores[uid]

        await message.answer(f"Баллы: {score}\n{get_result_text(score)}\n\n✍️ Введи имя для сертификата:"
        )

        user_states[uid] = {"stage": "cert"}

# --- СЕРТИФИКАТ ---
@dp.message(lambda m: user_states.get(m.from_user.id, {}).get("stage") == "cert")
async def cert(message: types.Message):
    name = message.text

    await message.answer("⏳ Делаю красиво...")

    img = await generate_certificate(name)

    await message.answer_photo(img, caption=f"🎓 Готово, {name}!")

    user_states[message.from_user.id] = {}
    await message.answer("Меню 👇", reply_markup=menu)

# --- ЗАПУСК ---
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
