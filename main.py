import telegram
from telegram.ext import Updater, CommandHandler
import requests
import time
import threading
from flask import Flask
from datetime import datetime
import pytz

# Telegram bot setup
TOKEN = "8178988656:AAElyrhMLCx8PKy4gGkO7mFB-W0b27ctuso"
URL = "https://idfc.dpdns.org/HSTR/api/cookie.php"
GROUP_CHAT_ID = "-1002505801351"  # Group ID

# Flask app for health check
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Bot is running", 200

def get_ist_time():
    # Get current time in IST (+05:30)
    ist = pytz.timezone("Asia/Kolkata")
    return datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S")

def start(update, context):
    chat_id = update.message.chat_id
    context.bot.send_message(chat_id=chat_id, text="Bot started! Checking URL now...")
    threading.Thread(target=check_url, args=(context,)).start()

def check_url(context):
    while True:
        try:
            response = requests.get(URL)
            cookies = response.cookies.get_dict()

            if not cookies:
                message = f"Cookies not founded resending request at {get_ist_time()}"
                context.bot.send_message(chat_id=GROUP_CHAT_ID, text=message)
                continue  # Resend request immediately
            else:
                cookie_names = cookies.keys()
                message = f"Cookies founded at {get_ist_time()}: {cookie_names}"
                context.bot.send_message(chat_id=GROUP_CHAT_ID, text=message)

                if "CloudFront-Key-Pair-Id" in cookie_names or "hdntl" in cookie_names:
                    context.bot.send_message(chat_id=GROUP_CHAT_ID, text="Found CloudFront-Key-Pair-Id or hdntl. Waiting 20 minutes...")
                    time.sleep(1200)  # Wait 20 minutes
                else:
                    context.bot.send_message(chat_id=GROUP_CHAT_ID, text="No specific cookies found. Checking again immediately...")
                    continue

        except Exception as e:
            context.bot.send_message(chat_id=GROUP_CHAT_ID, text=f"Error: {str(e)} at {get_ist_time()}. Retrying in 5 seconds...")
            time.sleep(5)

def run_bot():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=8080)).start()
    run_bot()
