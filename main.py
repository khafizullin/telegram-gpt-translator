
import os
import openai
from telegram import Update, Message
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
    print(f"[GPT] Отправка запроса на перевод:\n{prompt}")
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        translated = response['choices'][0]['message']['content'].strip()
        print(f"[GPT] Перевод получен:\n{translated}")
        return translated
    except Exception as e:
        print(f"[GPT] Ошибка при переводе: {e}")
        return "[Ошибка при переводе]"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message: Message = update.message
    if message is None or message.text is None:
        print("[SKIP] Пустое сообщение или не текст")
        return

    user_id = message.from_user.id
    chat_type = message.chat.type
    original = message.text

    print(f"[INCOMING] user_id={user_id}, chat_type={chat_type}, text={original}")

    if user_id == USER_1_ID:
        translated = await translate_message(original, "русского", "казахский")
        target_id = USER_2_ID
    elif user_id == USER_2_ID:
        translated = await translate_message(original, "казахского", "русский")
        target_id = USER_1_ID
    else:
        print(f"[SKIP] user_id={user_id} не входит в список разрешённых.")
        return

    reply = f"{translated}\n\n({original})"

    try:
        await context.bot.send_message(chat_id=target_id, text=reply)
        print(f"[SEND] Перевод отправлен user_id={target_id}")
    except Exception as e:
        print(f"[ERROR] Не удалось отправить сообщение user_id={target_id}: {e}")

app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
print("[START] Бот запущен")
app.run_polling()
