import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

TOKEN = "8585699588:AAH-7I3sS-iqKNmgYQ4MwweGAXOkTuQwT-A"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Хранилища
user_scores = {}
user_results = {}
user_states = {}
user_cert_data = {}
user_test_completed = {}

# ========== МЕНЮ ==========

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
        [KeyboardButton(text="📊 Мои результаты")],
        [KeyboardButton(text="🎓 Получить сертификат")]
    ],
    resize_keyboard=True
)

# ========== ВОПРОСЫ ==========

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

# Правильные ответы (для баллов)
correct_dict = {
    0: "Отнесу преподавателю потеряшку",
    1: "Случайную фразу: Красный_чайник_скачет_в_19:43",
    2: "Включи двухфакторную авторизацию",
    3: "Чтобы показать, где дыра в защите",
    4: "Может, вирус или майнер",
    5: "Вижу все уязвимости с первого взгляда"
}

def get_result_text(score: int) -> str:
    if score <= 5:
        return "🫣 Пока не очень подходит. Присмотрись к другим специальностям колледжа!"
    elif score <= 10:
        return "👍 Стоит попробовать! У тебя есть задатки."
    else:
        return "🔥 Отлично подходит! ОИБ — твоё направление!"

# ========== ТЕСТ ==========

@dp.message(lambda message: message.text == "🧠 Пройти тест")
async def start_test(message: types.Message):
    user_id = message.from_user.id
    user_scores[user_id] = 0
    user_results[user_id] = []
    user_states[user_id] = {"stage": "test", "question_index": 0}
    await send_question(message.chat.id, user_id)

async def send_question(chat_id: int, user_id: int):
    state = user_states.get(user_id)
    if state is None or state.get("stage") != "test":
        return
    index = state["question_index"]
    if index >= len(questions):
        await finish_test(chat_id, user_id)
        return
    question_text, options = questions[index]
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=opt) for opt in options]],
        resize_keyboard=True
    )
    await bot.send_message(chat_id, question_text, reply_markup=keyboard)

@dp.message(lambda message: user_states.get(message.from_user.id, {}).get("stage") == "test")
async def process_test_answer(message: types.Message):user_id = message.from_user.id
    state = user_states.get(user_id)
    if state is None or state.get("stage") != "test":
        return
    
    index = state["question_index"]
    if index >= len(questions):
        await finish_test(message.chat.id, user_id)
        return
    
    _, options = questions[index]
    if message.text not in options:
        await message.answer("Пожалуйста, выбери вариант из кнопок ниже.")
        return
    
    user_results[user_id].append(message.text)
    
    # Начисляем баллы за правильный ответ
    if message.text == correct_dict[index]:
        user_scores[user_id] = user_scores.get(user_id, 0) + 3
    
    state["question_index"] += 1
    if state["question_index"] < len(questions):
        await send_question(message.chat.id, user_id)
    else:
        await finish_test(message.chat.id, user_id)

async def finish_test(chat_id: int, user_id: int):
    user_test_completed[user_id] = True
    score = user_scores.get(user_id, 0)
    result_text = get_result_text(score)
    
    await bot.send_message(
        chat_id,
        f"🎉 **Тест завершён!**\n\n"
        f"📊 **Твои баллы: {score} из 18**\n\n"
        f"{result_text}\n\n"
        f"Теперь ты можешь получить сертификат! 🎓",
        reply_markup=menu_with_result
    )
    user_states[user_id] = {"stage": "idle"}

# ========== СЕРТИФИКАТ ==========

@dp.message(lambda message: message.text == "🎓 Получить сертификат")
async def start_certificate(message: types.Message):
    user_id = message.from_user.id
    if not user_test_completed.get(user_id, False):
        await message.answer("❌ Сертификат только после теста! Нажми «🧠 Пройти тест»", reply_markup=menu)
        return
    
    user_cert_data[user_id] = {}
    user_states[user_id] = {"stage": "cert_name"}
    await message.answer("🎓 Введите ваше ИМЯ:", reply_markup=types.ReplyKeyboardRemove())

@dp.message(lambda message: user_states.get(message.from_user.id, {}).get("stage") == "cert_name")
async def get_cert_name(message: types.Message):
    user_id = message.from_user.id
    user_cert_data[user_id]["name"] = message.text.strip()
    user_states[user_id] = {"stage": "cert_surname"}
    await message.answer("Теперь введите ФАМИЛИЮ:")

@dp.message(lambda message: user_states.get(message.from_user.id, {}).get("stage") == "cert_surname")
async def get_cert_surname(message: types.Message):
    user_id = message.from_user.id
    user_cert_data[user_id]["surname"] = message.text.strip()
    name = user_cert_data[user_id]["name"]
    surname = user_cert_data[user_id]["surname"]
    
    await message.answer(f"✅ Спасибо, {name} {surname}! Создаю сертификат...")
    await generate_and_send_certificate(message, name, surname)
    
    user_states[user_id] = {"stage": "idle"}
    del user_cert_data[user_id]

async def generate_and_send_certificate(message: types.Message, name: str, surname: str):
    template_path = "cert_template.jpeg"
    
    try:
        if not os.path.exists(template_path):
            await message.answer(
                f"🎉 **Поздравляем, {name} {surname}!**\n\n✅ Вы прошли тест!\n🏫 Ждём вас в ККРИТ!",
                reply_markup=menu_with_result
            )
            return
        
        from PIL import Image, ImageDraw, ImageFont
        
        img = Image.open(template_path)
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 60)
        except:
            font = ImageFont.load_default()
        
        width, height = img.size
        full_name = f"{name} {surname}"
        y = height // 2 + 50
        x = width // 3
        
        draw.text((x, y), full_name, fill="black", font=font)
        
        output_path = f"cert_{message.from_user.id}.jpeg"
        img.save(output_path, "JPEG")
        
        with open(output_path, "rb") as photo:
            await message.answer_photo(
                photo,
                caption=f"🎉 **Поздравляем, {name} {surname}!**\n\n✅ Вы прошли тест!\n🏫 Ждём вас в ККРИТ!",
                reply_markup=menu_with_result
            )os.remove(output_path)
        
    except Exception as e:
        await message.answer(
            f"🎉 **Поздравляем, {name} {surname}!**\n\n✅ Вы прошли тест!\n🏫 Ждём вас в ККРИТ!",
            reply_markup=menu_with_result
        )

# ========== ОСТАЛЬНЫЕ ОБРАБОТЧИКИ ==========

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "👋 Привет!\nЯ помогу тебе узнать о специальности\n"
        "«Основы информационной безопасности автоматизированных систем»\n\n"
        "🔐 Выбирай, что интересно 👇",
        reply_markup=menu
    )

@dp.message(lambda message: message.text == "📘 Что это за специальность")
async def info(message: types.Message):
    await message.answer(
        "🔐 **Основы информационной безопасности АС**\n\n"
        "Ты научишься:\n"
        "• Защищать сайты и базы данных\n"
        "• Шифровать информацию\n"
        "• Находить уязвимости\n"
        "• Работать с криптографией\n\n"
        "🔥 Одна из самых востребованных профессий!",
        reply_markup=menu
    )

@dp.message(lambda message: message.text == "💼 Где работать")
async def job(message: types.Message):
    await message.answer(
        "💼 **Где работать:**\n\n"
        "• Специалист по ИБ\n"
        "• Системный администратор\n"
        "• Аналитик безопасности\n"
        "• Этичный хакер\n"
        "• IT-специалист\n\n"
        "💰 Зарплата: от 80 000 ₽",
        reply_markup=menu
    )

@dp.message(lambda message: message.text == "📚 Специальности колледжа")
async def all_specialties(message: types.Message):
    text = (
        "📚 **Специальности нашего колледжа:**\n\n"
        "🔐 Основы информационной безопасности АС\n"
        "🧑‍💻 Специалист по компьютерным системам\n"
        "🧑‍🏭 Монтаж и техническое обслуживание\n"
        "📒 Бухгалтер\n"
        "🏦 Банковское дело\n"
        "🎨 Веб-разработка\n"
        "🎮 Разработчик компьютерных игр\n"
        "🤖 Специалист по работе с ИИ\n"
        "🚒 Пожарная безопасность\n\n"
        "✨ Ждём тебя на дне открытых дверей!"
    )
    await message.answer(text, reply_markup=menu)

@dp.message(lambda message: message.text == "📊 Мои результаты")
async def show_results(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_scores:
        await message.answer("Ты ещё не проходил тест. Нажми «🧠 Пройти тест»", reply_markup=menu)
        return
    score = user_scores[user_id]
    answers = user_results.get(user_id, [])
    text = f"📊 **Твой результат: {score} баллов из 18**\n\n📋 **Ответы:**\n"
    for i, ans in enumerate(answers, 1):
        text += f"{i}. {ans}\n"
    await message.answer(text, reply_markup=menu_with_result)

# ========== ЗАПУСК ==========

async def main():
    print("🤖 Бот запущен!")
    await dp.start_polling(bot)

if name == "__main__":
    asyncio.run(main())
