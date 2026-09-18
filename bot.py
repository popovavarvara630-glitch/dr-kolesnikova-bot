import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv

# Загружаем токен из .env файла
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Твой Telegram ID
ADMIN_ID = 1624451822  

# Настоящий юзернейм для связи
CONTACT_USERNAME = "doctor_kolesnikova"


# Описываем состояния для машины состояний (FSM)
class QuestionState(StatesGroup):
    waiting_for_question = State()


# --- ГЛАВНОЕ МЕНЮ И КНОПКИ ---
def get_main_menu():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="📅 Записаться на приём", callback_data="booking"))
    builder.row(types.InlineKeyboardButton(text="❓ Задать вопрос", callback_data="ask_question"))
    builder.row(types.InlineKeyboardButton(text="🧴 Подобрать уход", callback_data="choose_skin"))
    builder.row(types.InlineKeyboardButton(text="💰 Стоимость услуг", callback_data="price_list"))
    builder.row(types.InlineKeyboardButton(text="📍 Адрес", callback_data="location_info"))
    builder.row(types.InlineKeyboardButton(text="💡 Частые вопросы (FAQ)", callback_data="faq_menu"))
    builder.row(types.InlineKeyboardButton(text="✨ Обо мне", callback_data="about_me"))
    builder.row(types.InlineKeyboardButton(text="📞 Связаться со мной", url=f"https://t.me/{CONTACT_USERNAME}"))
    return builder.as_markup()


# --- СЛОВАРЬ РЕКОМЕНДАЦИЙ С БРЕНДАМИ ---
SKIN_RECOMMENDATIONS = {
    "skin_dry": (
        "🌿 **Бережный уход для сухой кожи:**\n\n"
        "Главная задача — восстановить защитный барьер и подарить коже глубокое питание.\n\n"
        "💧 **1. Очищение:**\n"
        "• *CeraVe Hydrating Cleanser* — классика на каждый день, бережно очищает без чувства стянутости.\n"
        "• *La Roche-Posay Toleriane Caring Wash* — ультрамягкий крем-гель.\n\n"
        "✨ **2. Активный уход и увлажнение:**\n"
        "• Сыворотка с церамидами и гиалуроновой кислотой *Anua Peach 70 Niacin Serum*.\n"
        "• Крем *CeraVe Facial Moisturizing Lotion* (с церамидами и ниацинамидом).\n\n"
        "🛡 **3. Защита:**\n"
        "• Питательный крем и легкий SPF на выход, чтобы удерживать влагу весь день."
    ),
    "skin_oily": (
        "🌿 **Баланс и чистота для жирной кожи:**\n\n"
        "Фокус на деликатное себорегулирование, борьбу с несовершенствами и качественное матовое увлажнение.\n\n"
        "🫧 **1. Очищение:**\n"
        "• *CeraVe Foaming Cleanser* с церамидами и ниацинамидом.\n"
        "• Гель для умывания *Cosrx Salicylic Acid Daily Gentle Cleanser* с мягкой BHA-кислотой.\n\n"
        "💧 **2. Уход и себорегуляция:**\n"
        "• Легкая сыворотка *The Ordinary Niacinamide 10% + Zinc 1%*.\n"
        "• Увлажняющий гель-крем *Isntree Hyaluronic Acid Aqua Gel Cream* (некомедогенно!).\n\n"
        "☀️ **3. Защита:**\n"
        "• Невесомый флюид с матирующим эффектом."
    ),
    "skin_comb": (
        "⚖️ **Гармония для комбинированной кожи:**\n\n"
        "Усмиряем блеск в Т-зоне и бережно заботимся о нормальных или сухих участках.\n\n"
        "🍃 **1. Очищение:**\n"
        "• Мягкий гель *Bioderma Sensibio Gel Moussant*.\n\n"
        "✨ **2. Уход:**\n"
        "• Увлажняющая эссенция или тонер с центеллой *Centella Asiatica*, например от бренда *Skin1004*.\n"
        "• Легкий крем, который быстро впитывается и не перегружает лицо.\n\n"
        "🌸 **3. Дополнительно:**\n"
        "• Энзимная пудра для мягкого отшелушивания Т-зоны 1–2 раза в неделю."
    ),
    "skin_sens": (
        "🌸 **Антистресс-уход для чувствительной кожи:**\n\n"
        "Минимум активов, максимум успокаивающих и восстанавливающих компонентов. Никакой агрессии!\n\n"
        "☁️ **1. Очищение:**\n"
        "• Успокаивающее молочко или пенка *La Roche-Posay Toleriane*.\n"
        "• Гидрофильное масло или бальзам для очень мягкого снятия макияжа.\n\n"
        "🌿 **2. Восстановление:**\n"
        "• Крем с пантенолом *La Roche-Posay Cicaplast Baume B5+* — палочка-выручалочка для раздраженной кожи.\n"
        "• Сыворотки с центеллой и аллантоином.\n\n"
        "🛡 **3. Защита:**\n"
        "• Гипоаллергенный крем с физическими фильтрами SPF."
    )
}


# --- СТАРТ И ГЛАВНОЕ МЕНЮ ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    print(f"[КОНСОЛЬ] Пользователь {message.from_user.full_name} (@{message.from_user.username}, ID: {message.from_user.id}) запустил бота.")
    await message.answer(
        "Приветствую! Я виртуальный помощник доктора Даши ✨\n\n"
        "Здесь ты можешь записаться на приём, подобрать профессиональный уход по типу кожи, узнать стоимость услуг и адрес, почитать частые вопросы или задать личный вопрос специалисту. Выбирай нужный раздел ниже:",
        reply_markup=get_main_menu()
    )


# --- КНОПКА «ЗАПИСАТЬСЯ НА ПРИЁМ» ---
@dp.callback_query(F.data == "booking")
async def process_booking(callback: types.CallbackQuery):
    print(f"[КОНСОЛЬ] {callback.from_user.full_name} открыл раздел записи на приём.")
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="💬 Написать лично для записи", url=f"https://t.me/{CONTACT_USERNAME}"))
    builder.row(types.InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="back_to_menu"))

    await callback.message.edit_text(
        "📅 **Запись на консультацию и приём**\n\n"
        "Чтобы выбрать удобное окошко и обсудить детали, нажми на кнопку ниже и напиши мне напрямую в личные сообщения. Я подберу комфортное время! ✨",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )
    await callback.answer()


# --- РАЗДЕЛ FAQ (ЧАСТЫЕ ВОПРОСЫ) ---
@dp.callback_query(F.data == "faq_menu")
async def process_faq_menu(callback: types.CallbackQuery):
    print(f"[КОНСОЛЬ] {callback.from_user.full_name} зашел в раздел FAQ.")
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="☀️ Нужен ли SPF зимой?", callback_data="faq_spf"))
    builder.row(types.InlineKeyboardButton(text="🚫 Можно ли давить прыщи?", callback_data="faq_acne"))
    builder.row(types.InlineKeyboardButton(text="✨ Нужно ли умываться до скрипа?", callback_data="faq_clean"))
    builder.row(types.InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="back_to_menu"))

    await callback.message.edit_text(
        "💡 **Частые вопросы и мифы об уходе**\n\n"
        "Выбирай интересующий вопрос, чтобы узнать мнение доказательной дерматологии: 👇",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("faq_"))
async def process_faq_answer(callback: types.CallbackQuery):
    faq_type = callback.data
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="⬅️ К списку вопросов", callback_data="faq_menu"))
    builder.row(types.InlineKeyboardButton(text="🏠 В главное меню", callback_data="back_to_menu"))

    if faq_type == "faq_spf":
        text = (
            "☀️ **Нужен ли SPF зимой?**\n\n"
            "**Да, нужен!** UVA-лучи (которые вызывают фотостарение и пигментацию) проходят сквозь тучи и стекло круглый год. Если ты используешь в уходе кислоты или ретинол, SPF обязателен даже в пасмурные зимние дни."
        )
    elif faq_type == "faq_acne":
        text = (
            "🚫 **Можно ли давить прыщи?**\n\n"
            "**Категорически нет!** Когда ты давишь воспаление, содержимое фолликула прорывается не только наружу, но и глубже в дерму. Это приводит к усилению воспаления, занесению инфекции, постакне и глубоким рубцам."
        )
    elif faq_type == "faq_clean":
        text = (
            "✨ **Нужно ли умываться до скрипа?**\n\n"
            "**Ни в коем случае!** «Скрип» означает, что вы полностью смыли защитный липидный слой кожи. Это разрушает защитный барьер, провоцирует обезвоженность, шелушения и... еще большее выделение себума (кожного сала)."
        )
    else:
        text = "Информация уточняется..."

    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="Markdown")
    await callback.answer()


# --- ЛОГИКА ВЫБОРА ТИПА КОЖИ ---
@dp.callback_query(F.data == "choose_skin")
async def process_choose_skin(callback: types.CallbackQuery):
    print(f"[КОНСОЛЬ] {callback.from_user.full_name} открыл подбор ухода.")
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🌿 Сухая кожа", callback_data="skin_dry"))
    builder.row(types.InlineKeyboardButton(text="🌿 Жирная кожа", callback_data="skin_oily"))
    builder.row(types.InlineKeyboardButton(text="⚖️ Комбинированная кожа", callback_data="skin_comb"))
    builder.row(types.InlineKeyboardButton(text="🌸 Чувствительная кожа", callback_data="skin_sens"))
    builder.row(types.InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="back_to_menu"))

    await callback.message.edit_text(
        "Выбери свой тип кожи, чтобы получить персональные рекомендации и подборку средств: 🧴",
        reply_markup=builder.as_markup()
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("skin_"))
async def process_skin_recommendation(callback: types.CallbackQuery):
    skin_type = callback.data
    print(f"[КОНСОЛЬ] {callback.from_user.full_name} запросил рекомендации для: {skin_type}")
    text = SKIN_RECOMMENDATIONS.get(skin_type, "Рекомендации подготавливаются...")
    
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="⬅️ К выбору типа кожи", callback_data="choose_skin"))
    builder.row(types.InlineKeyboardButton(text="🏠 В главное меню", callback_data="back_to_menu"))

    await callback.message.edit_text(
        text,
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )
    await callback.answer()


# --- КНОПКА «СТОИМОСТЬ УСЛУГ» (ПРАЙС) ---
@dp.callback_query(F.data == "price_list")
async def process_price_list(callback: types.CallbackQuery):
    print(f"[КОНСОЛЬ] {callback.from_user.full_name} открыл прайс-лист.")
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="📅 Записаться на приём", callback_data="booking"))
    builder.row(types.InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="back_to_menu"))

    await callback.message.edit_text(
        "💰 **Стоимость услуг и консультаций**\n\n"
        "🩺 **Первичная консультация дерматолога-косметолога**\n"
        "• Сбор анамнеза, оценка состояния кожи, постановка диагноза и составление базового плана ухода.\n"
        "• *Стоимость:* 3 500 ₽\n\n"
        "✨ **Повторная или контрольная консультация**\n"
        "• Оценка динамики лечения, коррекция назначений.\n"
        "• *Стоимость:* 2 500 ₽\n\n"
        "🧪 **Разбор домашнего ухода (аудит косметички)**\n"
        "• Разбор всех ваших баночек, проверка составов на комедогенность и конфликтность активов.\n"
        "• *Стоимость:* 2 000 ₽\n\n"
        "Выбирайте удобный формат, и давайте сделаем вашу кожу здоровой! 🌿",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )
    await callback.answer()


# --- КНОПКА «АДРЕС» ---
@dp.callback_query(F.data == "location_info")
async def process_location_info(callback: types.CallbackQuery):
    print(f"[КОНСОЛЬ] {callback.from_user.full_name} открыл раздел с адресом.")
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="📅 Записаться на приём", callback_data="booking"))
    builder.row(types.InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="back_to_menu"))

    await callback.message.edit_text(
        "📍 **Адрес приема**\n\n"
        "• г. Воронеж, ул. Машиностроителей, д. 82\n\n"
        "Жду вас на консультациях! 🌿",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )
    await callback.answer()


# --- КНОПКА «ОБО МНЕ» ---
@dp.callback_query(F.data == "about_me")
async def process_about_me(callback: types.CallbackQuery):
    print(f"[КОНСОЛЬ] {callback.from_user.full_name} открыл раздел «Обо мне».")
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="back_to_menu"))

    await callback.message.edit_text(
        "✨ **Колесникова Дарья Андреевна**\n\n"
        "Практикующий врач-косметолог и дерматолог. Моя главная цель — помочь вашей коже выглядеть здоровой, ухоженной и сияющей без изнуряющих процедур и лишних баночек на полке.\n\n"
        "🧪 **Мой подход:**\n"
        "• Исключительно доказательная медицина и безопасные методики.\n"
        "• Глубокий анализ проблемы, а не маскирование симптомов.\n"
        "• Индивидуальные схемы ухода, которые действительно работают.\n\n"
        "Здесь вы найдете бережную заботу о себе и профессиональный взгляд на вашу красоту. Добро пожаловать! 🌿",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )
    await callback.answer()


# --- ВОЗВРАТ В ГЛАВНОЕ МЕНЮ ---
@dp.callback_query(F.data == "back_to_menu")
async def process_back_to_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "Главное меню. Выбирай интересующий раздел:",
        reply_markup=get_main_menu()
    )
    await callback.answer()


# --- ЛОГИКА ЗАДАЧИ ВОПРОСА С ЗАЩИТОЙ И ФОТО (FSM) ---
@dp.callback_query(F.data == "ask_question")
async def process_ask_question(callback: types.CallbackQuery, state: FSMContext):
    print(f"[КОНСОЛЬ] {callback.from_user.full_name} начал процесс отправки вопроса.")
    await state.set_state(QuestionState.waiting_for_question)
    
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="⬅️ Отмена", callback_data="back_to_menu"))

    await callback.message.edit_text(
        "Каждый случай уникален, и мне важно разобрать твой вопрос лично. ✨\n\n"
        "Опиши то, что тебя беспокоит, и **обязательно прикрепи фото** кожи, если это возможно. Отправь всё одним сообщением!",
        reply_markup=builder.as_markup()
    )
    await callback.answer()


# Обработка корректного ввода (текст или фото)
@dp.message(QuestionState.waiting_for_question, F.photo | F.text)
async def receive_user_question(message: types.Message, state: FSMContext):
    user_name = message.from_user.full_name
    user_username = f"@{message.from_user.username}" if message.from_user.username else "не указан"
    user_id = message.from_user.id
    
    question_text = message.caption if message.caption else (message.text if message.text else "Без текста")
    print(f"[КОНСОЛЬ] Получен новый вопрос от пользователя {user_name} (ID: {user_id})")
    
    admin_notification = (
        f"📩 **Новый вопрос с медиа!**\n\n"
        f"👤 **Имя:** {user_name} ({user_username})\n"
        f"🆔 **ID:** `{user_id}`\n\n"
        f"💬 **Текст/Описание:**\n{question_text}"
    )
    
    try:
        if message.photo:
            photo_file_id = message.photo[-1].file_id
            await bot.send_photo(
                ADMIN_ID, 
                photo=photo_file_id, 
                caption=admin_notification, 
                parse_mode="Markdown"
            )
        else:
            await bot.send_message(ADMIN_ID, admin_notification, parse_mode="Markdown")
            
    except Exception as e:
        print(f"[ОШИБКА] Не удалось отправить сообщение админу: {e}")
    
    await message.answer(
        "Спасибо! Твое сообщение и фото успешно отправлены доктору Даше. Она скоро изучит их и ответит тебе. ✨"
    )
    await state.clear()


# Защита от дурака: если прислали стикер, аудио, документ или гифку вместо текста/фото
@dp.message(QuestionState.waiting_for_question)
async def invalid_question_input(message: types.Message):
    print(f"[КОНСОЛЬ] Пользователь прислал неподдерживаемый формат в режиме вопроса.")
    await message.answer(
        "Пожалуйста, отправь свой вопрос **текстом** или прикрепи **фотографию** кожи. Голосовые сообщения, стикеры или файлы сейчас обработать не получится ✨"
    )


# --- ЗАПУСК БОТА ---
async def main():
    print("Бот запущен и работает в штатном режиме...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())