import telegram
from telegram.ext import Updater, CommandHandler
import requests
import time
import threading
from flask import Flask

# Telegram bot setup
TOKEN = "8178988656:AAElyrhMLCx8PKy4gGkO7mFB-W0b27ctuso"
URL = "https://idfc.dpdns.org/HSTR/api/cookie.php"

# Flask app for health check
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Bot is running", 200

def start(update, context):
    chat_id = update.message.chat_id
    context.bot.send_message(chat_id=chat_id, text="Bot started! Checking URL now...")
    threading.Thread(target=check_url, args=(context, chat_id)).start()

def check_url(context, chat_id):
    while True:
        try:
            response = requests.get(URL)
            cookies = response.cookies.get_dict()

            if not cookies:
                context.bot.send_message(chat_id=chat_id, text="No cookies found. Resending request immediately...")
                continue
            else:
                cookie_names = cookies.keys()
                message = f"Cookies found: {cookie_names}"
                context.bot.send_message(chat_id=chat_id, text=message)

                if "CloudFront-Key-Pair-Id" in cookie_names or "hdntl" in cookie_names:
                    context.bot.send_message(chat_id=chat_id, text="Found CloudFront-Key-Pair-Id or hdntl. Waiting 20 minutes...")
                    time.sleep(1200)
                else:
                    context.bot.send_message(chat_id=chat_id, text="No specific cookies found. Checking again immediately...")
                    continue

        except Exception as e:
            context.bot.send_message(chat_id=chat_id, text=f"Error: {str(e)}. Retrying in 5 seconds...")
            time.sleep(5)

def run_bot():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    # Start Flask in a separate thread
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=8080)).start()
    # Start the Telegram bot
    run_bot()
