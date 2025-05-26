import os
import openai
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
USER_1_ID = int(os.getenv("USER_1_ID", "0"))
USER_2_ID = int(os.getenv("USER_2_ID", "0"))

openai.api_key = OPENAI_API_KEY

async def translate_message(message_text, source_lang, target_lang):
    prompt = (
        f"Переведи с {source_lang} на {target_lang}, соблюдая следующие правила:\n"
        "- Передавай стиль, форму, наклонение и намерение говорящего.\n"
        "- Не меняй интонацию (если приказ — пусть остаётся приказом).\n"
        "- Не интерпретируй чувства и не добавляй мягкости.\n"
        "- Исправляй только ошибки, но не искажай смысл.\n"
        "Текст:\n" + message_text
    )
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response['choices'][0]['message']['content'].strip()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    original = update.message.text
    user_id = update.message.from_user.id

    if user_id == USER_1_ID:
        translated = await translate_message(original, "русского", "казахский")
    elif user_id == USER_2_ID:
        translated = await translate_message(original, "казахского", "русский")
    else:
        translated = "Извините, вы не зарегистрированы для перевода."

    reply = f"{translated}\n\n({original})"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=reply)

app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.run_polling()
