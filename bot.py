import asyncio
import os
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

# ВСТАВЬ СВОЙ ТОКЕН:
TOKEN = "8720318790:AAHr7llBYcQJBm1iGhm1jmYHjdbIONXncGQ"

bot = Bot(token=TOKEN)
dp = Dispatcher()

user_scores = {}
user_results = {}
user_states = {}  # Для отслеживания состояния пользователя
user_cert_data = {}
user_test_completed = {}

# Главное меню
menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📘 Что это за специальность")],
        [KeyboardButton(text="💼 Где работать")],
        [KeyboardButton(text="🧠 Пройти тест")],
        [KeyboardButton(text="📚 Специальности колледжа")]
        [KeyboardButton(text="🎓 Получить сертификат")]
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

# Правильные ответы и баллы
correct_answers = {
    0: ("Отнесу преподавателю/потеряшку", 3),
    1: ("Случайную фразу: Красный_чайник_скачет_в_19:43", 3),
    2: ("Включи двухфакторную авторизацию", 3),
    3: ("Чтобы показать, где дыра в защите", 3),
    4: ("Может, вирус или майнер", 3),
    5: ("Вижу все уязвимости с первого взгляда", 3)
}

def get_result_text(score: int) -> str:
    """Возвращает текст результата по количеству баллов"""
    if score <= 5:
        return "🫣 Пока не очень подходит. Присмотрись к другим специальностям колледжа!"
    elif score <= 10:
        return "👍 Стоит попробовать! У тебя есть задатки."
    else:
        return "🔥 Отлично подходит! ОИБ — твоё направление!"
# ========== ТЕСТ (БЕЗ ПРОВЕРКИ, БЕЗ КНОПКИ "В ГЛАВНОЕ МЕНЮ") ==========

@dp.message(lambda message: message.text == "🧠 Пройти тест")
async def start_test(message: types.Message):
    user_id = message.from_user.id
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
async def process_test_answer(message: types.Message):
    user_id = message.from_user.id
    state = user_states.get(user_id)
    
    if state is None or state.get("stage") != "test":
        return
    
    index = state["question_index"]
    if index >= len(questions):
        await finish_test(message.chat.id, user_id)
        return
    
    question_text, options = questions[index]
    
    if message.text not in options:
        await message.answer("Пожалуйста, выбери вариант из кнопок ниже.")
        return
    
    # Сохраняем ответ
    user_results[user_id].append(message.text)
    
    # Следующий вопрос
    state["question_index"] += 1
    
    if state["question_index"] < len(questions):
        await send_question(message.chat.id, user_id)
    else:
        await finish_test(message.chat.id, user_id)

async def finish_test(chat_id: int, user_id: int):
    user_test_completed[user_id] = True
    
    await bot.send_message(
        chat_id,
        f"🎉 **Тест завершён!**\n\n"
        f"Спасибо за участие!\n\n"
        f"Теперь ты можешь получить свой сертификат! 🎓",
        reply_markup=menu_with_result
    )
    user_states[user_id] = {"stage": "idle"}

# ========== СЕРТИФИКАТ ==========

@dp.message(lambda message: message.text == "🎓 Получить сертификат")
async def start_certificate(message: types.Message):
    user_id = message.from_user.id
    
    if not user_test_completed.get(user_id, False):
        await message.answer(
            "❌ Сертификат выдаётся только после прохождения теста!\n\n"
            "Сначала пройди тест: «🧠 Пройти тест»",
            reply_markup=menu
        )
        return
    
    user_cert_data[user_id] = {}
    user_states[user_id] = {"stage": "cert_name"}
    await message.answer(
        "🎓 **Оформление сертификата**\n\n"
        "Введите ваше ИМЯ:",
        reply_markup=types.ReplyKeyboardRemove()
    )

@dp.message(lambda message: user_states.get(message.from_user.id, {}).get("stage") == "cert_name")
async def get_cert_name(message: types.Message):
    user_id = message.from_user.id
    user_cert_data[user_id]["name"] = message.text.strip()
    user_states[user_id] = {"stage": "cert_surname"}
    await message.answer("Теперь введите вашу ФАМИЛИЮ:")

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
            await message.answer("❌ Шаблон сертификата не найден.")
            return
        
        from PIL import Image, ImageDraw, ImageFont
        
        img = Image.open(template_path)
        draw = ImageDraw.Draw(img)
        
        try:
            font_name = ImageFont.truetype("arial.ttf", 80)
            font_surname = ImageFont.truetype("arial.ttf", 60)
        except:
            font_name = ImageFont.load_default()
            font_surname = ImageFont.load_default()
        
        # Координаты для имени и фамилии (подгони под свой шаблон)
        draw.text((400, 350), name, fill="black", font=font_name)
        draw.text((400, 450), surname, fill="black", font=font_surname)
        
        output_path = f"cert_{message.from_user.id}.jpeg"
        img.save(output_path, "JPEG")
        
        with open(output_path, "rb") as photo:
            await message.answer_photo(
                photo,
                caption=f"🎉 **Поздравляем, {name} {surname}!**\n\n"
                        f"✅ Вы успешно прошли тест!\n"
                        f"🏫 Ждём вас в ККРИТ!",
                reply_markup=menu_with_result
            )
        
        os.remove(output_path)
        
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")
        print(f"Certificate error: {e}")
# Система картинок по номеру
image_urls = {
    1: "https://cdn.pixabay.com/photo/2016/11/23/14/45/coding-1853305_960_720.jpg",
    2: "https://cdn.pixabay.com/photo/2015/05/29/19/17/study-789631_1280.jpg",
}

image_section_map = {
    "specialty": 1,
    "job": 2,
    "test": 3
}


def get_image_url(image_id: int) -> str:
    return image_urls.get(image_id, image_urls[1])


def get_image_id(section: str | int) -> int:
    if isinstance(section, int):
        return section if section in image_urls else 1
    return image_section_map.get(section.lower(), 1)


def get_image_id_from_url(url: str) -> int:
    for image_id, image_url in image_urls.items():
        if image_url == url:
            return image_id
    return 1


async def answer_photo_safe(message: types.Message, photo: str, caption: str, reply_markup):
    try:
        await message.answer_photo(
            photo=photo,
            caption=caption,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        return
    except Exception:
        fallback_photo = "https://picsum.photos/800/600"
        try:
            await message.answer_photo(
                photo=fallback_photo,
                caption=caption,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
            return
        except Exception:
            pass

    await message.answer(caption, reply_markup=reply_markup, parse_mode="Markdown")


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
        photo=get_image_url(get_image_id("specialty")),
        caption=(
            "🔐 **Основы информационной безопасности АС**\n\n"
            "Ты научишься:\n"
            "• Защищать сайты и базы данных\n"
            "• Шифровать информацию\n"
            "• Находить уязвимости\n"
            "• Работать с криптографией\n\n"
            "🔥 Одна из самых востребованных профессий!"
        ),
        reply_markup=menu
    )

@dp.message(lambda message: message.text == "💼 Где работать")
async def job(message: types.Message):
    caption = (
        "💼 **Где работать:**\n\n"
        "• Специалист по ИБ\n"
        "• Системный администратор\n"
        "• Аналитик безопасности\n"
        "• Этичный хакер\n"
        "• IT-специалист\n\n"
        "💰 Зарплата: от 80 000 ₽"
    )
    await answer_photo_safe(
        message,
        photo=get_image_url(get_image_id("job")),
        caption=caption,
        reply_markup=menu
    )

@dp.message(lambda message: message.text == "📚 Специальности колледжа")
async def all_specialties(message: types.Message):
    text = (
        "📚 Специальности нашего колледжа:\n\n"
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

@dp.message(lambda message: message.text == "🧠 Пройти тест")
async def start_test(message: types.Message):
    
    user_id = message.from_user.id
    user_scores[user_id] = 0
    user_results[user_id] = []
    user_states[user_id] = {"stage": "test", "question_index": 0}
    await send_question(message.chat.id, user_id)

async def send_question(chat_id: int, user_id: int):
    state = user_states.get(user_id)
    if state is None:
        return
    index = state["question_index"]
    if index >= len(questions):
        return
    question_text, options = questions[index]
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=option)] for option in options] + [[KeyboardButton(text="В главное меню")]],
        resize_keyboard=True
    )
    await bot.send_message(chat_id, question_text, reply_markup=keyboard)

@dp.message(lambda message: user_states.get(message.from_user.id, {}).get("stage") == "test")
async def process_test_answer(message: types.Message):
    user_id = message.from_user.id
    state = user_states.get(user_id)
    if state is None:
        return
    selected = message.text
    if selected in {"⏪ Главное меню", "В главное меню"}:
        user_states[user_id] = {"stage": "idle"}
        await message.answer("Ты вернулся в главное меню.", reply_markup=menu)
        return

    index = state["question_index"]
    if index >= len(questions):
        return
    question_text, options = questions[index]
    if selected not in options:
        await message.answer("Пожалуйста, выбери вариант из клавиатуры.")
        return

    user_results[user_id].append(selected)
    await message.answer(feedback)

    state["question_index"] += 1
    if state["question_index"] < len(questions):
        await send_question(message.chat.id, user_id)
    else:
        score = user_scores.get(user_id, 0)
        result_text = get_result_text(score)
        await message.answer(
            f"Тест завершён! Ты набрал {score} баллов.\n\n{result_text}",
            reply_markup=menu_with_result
        )
        user_states[user_id] = {"stage": "idle"}

@dp.message(lambda message: message.text == "📊 Мои результаты")
async def show_results(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_scores:
        await message.answer("Ты ещё не проходил тест. Нажми «🧠 Пройти тест».", reply_markup=menu)
        return
    score = user_scores[user_id]
    answers = user_results.get(user_id, [])
    await message.answer(
        f"Твой результат: {score} баллов.\nОтветы: {', '.join(answers)}",
        reply_markup=menu_with_result
    )

@dp.message(lambda message: message.text in {"⏪ Главное меню", "В главное меню"})
async def back_to_menu(message: types.Message):
    user_id = message.from_user.id
    user_states[user_id] = {"stage": "idle"}
    await message.answer("Ты вернулся в главное меню.", reply_markup=menu)

async def main():
    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        pass
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
