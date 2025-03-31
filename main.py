import time
import requests
import telebot

# Telegram bot token and chat ID
TELEGRAM_ACCESS_TOKEN = '8178988656:AAElyrhMLCx8PKy4gGkO7mFB-W0b27ctuso'
CHAT_ID = '-1002505801351'

# URL to send requests
URL = 'https://idfc.dpdns.org/HSTR/api/cookie.php'

# Initialize the bot
bot = telebot.TeleBot(TELEGRAM_ACCESS_TOKEN)

# Send request to the URL and check cookies
def send_request():
    try:
        response = requests.get(URL)
        cookies = response.cookies.get_dict()
        
        if not cookies:
            bot.send_message(CHAT_ID, '❌ No cookies found. Retrying in 5 seconds...')
            return False
        
        # Check for required cookies
        if 'CloudFront-Key-Pair-Id' in cookies or 'hdntl' in cookies:
            bot.send_message(CHAT_ID, '✅ Cookies found. Waiting 15 minutes before the next request...')
            time.sleep(900)  # 900 seconds = 15 minutes
        else:
            bot.send_message(CHAT_ID, '⚠️ Cookies found, but target cookies are missing. Retrying...')
            return False
        
        return True
    
    except requests.RequestException as e:
        bot.send_message(CHAT_ID, f'❗ Error: {str(e)}')
        return False

# Main loop to keep the bot running
while True:
    if not send_request():
        time.sleep(5)  # Retry after 5 seconds if cookies are not found
