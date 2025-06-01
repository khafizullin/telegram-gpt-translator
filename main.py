
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

# Логируем полученные переменные
print(f"[BOOT] BOT_TOKEN: {'✔️' if BOT_TOKEN else '❌'}")
print(f"[BOOT] OPENAI_API_KEY: {'✔️' if OPENAI_API_KEY else '❌'}")
print(f"[BOOT] USER_1_ID: {USER_1_ID}, USER_2_ID: {USER_2_ID}")

# Настраиваем OpenAI
openai.api_key = OPENAI_API_KEY

# Удаляем старый webhook
requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook")
print("[BOT] Webhook удалён")

# Функция перевода
async def translate_message(text, source_lang, target_lang):
    prompt = (
        f"Переведи с {source_lang} на {target_lang}, соблюдая следующие правила:\n"
        "- Передавай стиль, форму, наклонение и намерение говорящего.\n"
        "- Не меняй интонацию.\n"
        "- Не добавляй ничего от себя.\n"
        "- Только перевод, без пояснений.\n"
        "Текст:\n" + text
    )
    print(f"[GPT] Отправка запроса на перевод...")
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        translated = response['choices'][0]['message']['content'].strip()
        print(f"[GPT] Перевод: {translated}")
        return translated
    except Exception as e:
        print(f"[GPT ❌] Ошибка: {e}")
        return "[Ошибка при переводе]"

# Обработка сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    user_id = message.from_user.id
    text = message.text

    print(f"[INCOMING] user_id={user_id}, text={text}")

    if user_id == USER_1_ID:
        translated = await translate_message(text, "русского", "казахский")
        target_id = USER_2_ID
    elif user_id == USER_2_ID:
        translated = await translate_message(text, "казахского", "русский")
        target_id = USER_1_ID
    else:
        print("[SKIP] Пользователь не зарегистрирован")
        return

    reply = f"{translated}\n\n({text})"
    await context.bot.send_message(chat_id=target_id, text=reply)
    print(f"[SEND] Перевод отправлен user_id={target_id}")

# Запуск бота
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
print("[START] Бот запущен")
app.run_polling()
