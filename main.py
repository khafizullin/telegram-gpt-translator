import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from openai import OpenAI

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Получаем переменные окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
USER_1_ID = int(os.getenv("USER_1_ID"))
USER_2_ID = int(os.getenv("USER_2_ID"))

# Инициализируем OpenAI клиент
client = OpenAI(api_key=OPENAI_API_KEY)

# Функция перевода
async def translate_message(text, source_lang, target_lang):
    prompt = (
        f"Переведите с {source_lang} на {target_lang}, соблюдая следующие правила:\n"
        "- Передавайте стиль, форму, наклонение и намерение говорящего.\n"
        "- Не меняй интонацию.\n"
        "- Не добавляй ничего от себя.\n"
        "- Только перевод, без пояснений.\n"
        f"Текст:\n{text}"
    )
    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        return completion.choices[0].message.content
    except Exception as e:
        logging.error(f"Ошибка при переводе: {e}")
        return "[Ошибка при переводе]"

# Обработка сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.text:
        return

    user_id = message.from_user.id
    chat_id = message.chat.id
    text = message.text

    if user_id == USER_1_ID:
        source_lang = "русского"
        target_lang = "казахский"
    elif user_id == USER_2_ID:
        source_lang = "казахского"
        target_lang = "русский"
    else:
        logging.info(f"Неавторизованный пользователь: {user_id}")
        return

    translated = await translate_message(text, source_lang, target_lang)
    await context.bot.send_message(chat_id=chat_id, text=translated)

# Запуск бота
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()