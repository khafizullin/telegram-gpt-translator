
import os
import requests
import openai
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# Получаем переменные окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
USER_1_ID = int(os.getenv("USER_1_ID"))
USER_2_ID = int(os.getenv("USER_2_ID"))

# Настраиваем OpenAI
openai.api_key = OPENAI_API_KEY

# Удаляем старый webhook
requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook")

# Функция перевода текста
async def translate_message(text, source_lang, target_lang):
    prompt = (
        f"Переведи с {source_lang} на {target_lang}, соблюдая следующие правила:\n"
        "- Передавай стиль, форму, наклонение и намерение говорящего.\n"
        "- Не меняй интонацию.\n"
        "- Не добавляй ничего от себя.\n"
        "- Только перевод, без пояснений.\n"
        "Текст:\n" + text
    )
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response['choices'][0]['message']['content'].strip()

# Обработка сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    user_id = message.from_user.id
    text = message.text

    if user_id == USER_1_ID:
        translated = await translate_message(text, "русского", "казахский")
        target_id = USER_2_ID
    elif user_id == USER_2_ID:
        translated = await translate_message(text, "казахского", "русский")
        target_id = USER_1_ID
    else:
        return  # игнорируем других

    reply = f"{translated}\n\n({text})"
    await context.bot.send_message(chat_id=target_id, text=reply)

# Запуск бота
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.run_polling()
