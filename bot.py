import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

# ВСТАВЬ СВОЙ ТОКЕН:
TOKEN = "8720318790:AAFVck6JCTWHibWmCGf0kcV473McJchKrMg"

bot = Bot(token=TOKEN)
dp = Dispatcher()

user_scores = {}
user_results = {}
user_states = {}

# Главное меню
menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📘 Что это за специальность")],
        [KeyboardButton(text="💼 Где работать")],
        [KeyboardButton(text="🧠 Пройти тест")],
        [KeyboardButton(text="📚 Специальности колледжа")]
    ],
    resize_keyboard=True
)

# Меню после теста
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

questions = [
    ("Ты нашел флешку в коридоре колледжа. Твои действия?", [
        "Вставлю в свой комп — вдруг там что-то интересное",
        "Отнесу преподавателю потеряшку",
        "Выброшу, мало ли вирусы"
    ]),
    ("Придумай пароль для почты. Что выберешь?", [
        "qwerty123 — легко запомнить",
        "Имя кота + год рождения мамы",
        "Случайную фразу: Красный_чайник_скачет_в_19:43"
    ]),
    ("Друг говорит: «Мой аккаунт взломали!» Твой первый совет?", [
        "Срочно поменяй пароль на новый!",
        "Включи двухфакторную авторизацию",
        "Напиши хакеру в ответ, пусть вернет"
    ]),
    ("Как думаешь, зачем хакеры вообще взламывают системы?", [
        "Чтобы украсть деньги или данные",
        "Ради спортивного интереса и славы",
        "Чтобы показать, где дыра в защите"
    ]),
    ("Ты замечаешь, что компьютер стал тормозить. Что заподозришь первым делом?", [
        "Слишком много программ открыто",
        "Может, вирус или майнер",
        "Пора покупать новый комп"
    ]),
    ("Представь: ты — супергерой кибербезопасности. Какая у тебя суперсила?", [
        "Вижу все уязвимости с первого взгляда",
        "Могу зашифровать что угодно",
        "Нахожу хакеров по их следам в сети"
    ])
]

correct_answers = {
    0: ("Отнесу преподавателю потеряшку", 3),
    1: ("Случайную фразу: Красный_чайник_скачет_в_19:43", 3),
    2: ("Включи двухфакторную авторизацию", 3),
    3: ("Чтобы показать, где дыра в защите", 3),
    4: ("Может, вирус или майнер", 3),
    5: ("Вижу все уязвимости с первого взгляда", 3)
}

def get_result_text(score: int) -> str:
    if score <= 5:
        return "🫣 Пока не очень подходит. Присмотрись к другим специальностям колледжа!"
    elif score <= 10:
        return "👍 Стоит попробовать! У тебя есть задатки."
    else:
        return "🔥 Отлично подходит! ОИБ — твоё направление!"

image_urls = {
    1: "https://cdn.pixabay.com/photo/2016/11/23/14/45/coding-1853305_960_720.jpg",
    2: "https://cdn.pixabay.com/photo/2015/05/29/19/17/study-789631_1280.jpg",
    3: "https://cdn.pixabay.com/photo/2019/03/08/16/20/monkey-4042658_1280.jpg"
}

def get_image_url(image_id: int) -> str:
    return image_urls.get(image_id, image_urls[1])


async def answer_photo_safe(message: types.Message, photo: str, caption: str, reply_markup):
    try:
        await message.answer_photo(photo=photo, caption=caption, reply_markup=reply_markup)
    except Exception:
        await message.answer(caption, reply_markup=reply_markup)


@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "👋 Привет!\n"
        "Я помогу тебе узнать о специальности\n"
        "«Основы информационной безопасности автоматизированных систем»\n\n"
        "🔐 Выбирай, что интересно 👇",
        reply_markup=menu
    )


@dp.message(lambda message: message.text == "📘 Что это за специальность")
async def info(message: types.Message):
    await answer_photo_safe(
        message,
        photo=get_image_url(1),caption="🔐 Основы информационной безопасности АС\n\nТы научишься защищать данные и системы 🔥",
        reply_markup=menu
    )


@dp.message(lambda message: message.text == "💼 Где работать")
async def job(message: types.Message):
    await answer_photo_safe(
        message,
        photo=get_image_url(2),
        caption="💼 Специалист по ИБ, аналитик, админ и др.\n💰 от 80 000 ₽",
        reply_markup=menu
    )


@dp.message(lambda message: message.text == "📚 Специальности колледжа")
async def all_specialties(message: types.Message):
    await message.answer("📚 Есть много IT и не только направлений!", reply_markup=menu)


# 🔥 Показ картинки перед тестом
@dp.message(lambda message: message.text == "🧠 Пройти тест")
async def show_test_start(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🚀 Начать тест")],
            [KeyboardButton(text="В главное меню")]
        ],
        resize_keyboard=True
    )

    await message.answer_photo(
        photo=get_image_url(3),
        caption="🐒 Готов проверить себя?\n\nНажми «Начать тест» 👇",
        reply_markup=keyboard
    )


# 🚀 Старт теста
@dp.message(lambda message: message.text == "🚀 Начать тест")
async def start_test(message: types.Message):
    user_id = message.from_user.id
    user_scores[user_id] = 0
    user_results[user_id] = []
    user_states[user_id] = {"stage": "test", "question_index": 0}

    await send_question(message.chat.id, user_id)


async def send_question(chat_id: int, user_id: int):
    state = user_states.get(user_id)
    if not state:
        return

    index = state["question_index"]

    if index >= len(questions):
        return

    question_text, options = questions[index]

    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=opt)] for opt in options] + [[KeyboardButton(text="В главное меню")]],
        resize_keyboard=True
    )

    await bot.send_message(chat_id, question_text, reply_markup=keyboard)


@dp.message(lambda message: user_states.get(message.from_user.id, {}).get("stage") == "test")
async def process_test_answer(message: types.Message):
    user_id = message.from_user.id
    state = user_states.get(user_id)

    if not state:
        return

    if message.text == "В главное меню":
        user_states[user_id] = {"stage": "idle"}
        await message.answer("Ты вернулся в меню", reply_markup=menu)
        return

    index = state["question_index"]
    question_text, options = questions[index]

    if message.text not in options:
        await message.answer("Выбери вариант с кнопки")
        return

    user_results[user_id].append(message.text)

    # ✅ начисление баллов
    correct_text, points = correct_answers.get(index, ("", 0))
    if message.text == correct_text:
        user_scores[user_id] += points

    state["question_index"] += 1

    if state["question_index"] < len(questions):
        await send_question(message.chat.id, user_id)
    else:
        score = user_scores[user_id]
        result_text = get_result_text(score)

        await message.answer(
            f"Тест завершён!\nБаллы: {score}\n\n{result_text}",
            reply_markup=menu_with_result
        )

        user_states[user_id] = {"stage": "idle"}


@dp.message(lambda message: message.text == "📊 Мои результаты")
async def show_results(message: types.Message):
    user_id = message.from_user.id

    if user_id not in user_scores:
        await message.answer("Ты ещё не проходил тест", reply_markup=menu)
        return

    await message.answer(
        f"Баллы: {user_scores[user_id]}",
        reply_markup=menu_with_result
    )


@dp.message(lambda message: message.text == "В главное меню")
async def back(message: types.Message):
    user_states[message.from_user.id] = {"stage": "idle"}
    await message.answer("Главное меню", reply_markup=menu)


async def main():
    await dp.start_polling(bot)


if name == "__main__":
    asyncio.run(main())
