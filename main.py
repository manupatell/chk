import telegram
from telegram.ext import Application, CommandHandler
import requests
import time
import threading
from flask import Flask
from datetime import datetime
import pytz
import asyncio

# Configuration
TOKEN = "8178988656:AAElyrhMLCx8PKy4gGkO7mFB-W0b27ctuso"
URL = "https://idfc.dpdns.org/HSTR/api/cookie.php"
GROUP_CHAT_ID = "-1004651056352"  # Group ID

# Flask app for Koyeb health check
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Bot is running", 200

def get_ist_time():
    # Get current time in IST (+05:30)
    ist = pytz.timezone("Asia/Kolkata")
    return datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S")

async def send_startup_message(bot):
    # Send "Bot started" message to the group
    message = f"Bot started at {get_ist_time()}"
    await bot.send_message(chat_id=GROUP_CHAT_ID, text=message)

async def check_url(application):
    bot = application.bot
    while True:
        try:
            response = requests.get(URL, timeout=10)
            cookies = response.cookies.get_dict()

            if not cookies:
                message = f"Cookies not founded resending request at {get_ist_time()}"
                await bot.send_message(chat_id=GROUP_CHAT_ID, text=message)
                time.sleep(1)
            else:
                cookie_names = cookies.keys()
                message = f"Cookies founded at {get_ist_time()}: {cookie_names}"
                await bot.send_message(chat_id=GROUP_CHAT_ID, text=message)

                if "CloudFront-Key-Pair-Id" in cookie_names or "hdntl" in cookie_names:
                    await bot.send_message(chat_id=GROUP_CHAT_ID, text="Found CloudFront-Key-Pair-Id or hdntl. Waiting 20 minutes...")
                    time.sleep(1200)
                else:
                    await bot.send_message(chat_id=GROUP_CHAT_ID, text="No specific cookies found. Checking again immediately...")
                    time.sleep(1)

        except requests.RequestException as e:
            await bot.send_message(chat_id=GROUP_CHAT_ID, text=f"Request error: {str(e)} at {get_ist_time()}. Retrying in 5 seconds...")
            time.sleep(5)
        except telegram.error.TelegramError as e:
            await bot.send_message(chat_id=GROUP_CHAT_ID, text=f"Telegram error: {str(e)} at {get_ist_time()}. Retrying in 5 seconds...")
            time.sleep(5)
        except Exception as e:
            await bot.send_message(chat_id=GROUP_CHAT_ID, text=f"Unexpected error: {str(e)} at {get_ist_time()}. Retrying in 5 seconds...")
            time.sleep(5)

async def start(update, context):
    await update.message.reply_text("Bot is running 24/7. Check group for updates!")

def run_bot():
    # Initialize the application
    application = Application.builder().token(TOKEN).build()
    
    # Add command handler
    application.add_handler(CommandHandler("start", start))

    # Send startup message
    asyncio.run(send_startup_message(application.bot))

    # Start URL checking in a separate thread
    threading.Thread(target=lambda: application.run_async(check_url, application), daemon=True).start()

    # Start polling
    application.run_polling()

if __name__ == "__main__":
    # Start Flask in a separate thread for Koyeb health check
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=8080), daemon=True).start()
    run_bot()
