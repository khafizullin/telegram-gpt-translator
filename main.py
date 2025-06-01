
import logging
import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Настройки логов
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Получаем переменные окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
USER_1_ID = int(os.getenv("USER_1_ID"))
USER_2_ID = int(os.getenv("USER_2_ID"))

# Удаляем webhook перед запуском polling
requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook")

# Функция обработки сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender_id = update.effective_user.id
    message = update.message.text
    receiver_id = USER_2_ID if sender_id == USER_1_ID else USER_1_ID
    await context.bot.send_message(chat_id=receiver_id, text=message)

# Основной запуск
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
