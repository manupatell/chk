import time
import requests
import telebot

# Telegram bot token
TELEGRAM_ACCESS_TOKEN = '7436905134:AAGltfbb1IiNzKZSiYVJDJv4v8r8sJprVJw'
CHAT_ID = '@fancodema'

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
            bot.send_message(CHAT_ID, 'No cookies found. Retrying...')
            return False
        
        # Check if required cookies are present
        if 'CloudFront-Key-Pair-Id' in cookies or 'hdntl' in cookies:
            bot.send_message(CHAT_ID, 'Cookies found. Waiting 15 mins...')
            time.sleep(900)  # Wait 15 mins
        else:
            bot.send_message(CHAT_ID, 'No target cookies found. Retrying...')
            return False
        
        return True
    
    except Exception as e:
        bot.send_message(CHAT_ID, f'Error: {str(e)}')
        return False

# Main loop to keep the bot running
while True:
    if not send_request():
        time.sleep(5)  # Retry after 5 seconds if cookies are not found
