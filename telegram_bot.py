import requests
import os
from dotenv import load_dotenv

# Завантаження змінних з .env
load_dotenv()

# Отримання токена і chat_id з оточення
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Основна функція для надсилання повідомлення
def send_telegram_message(text):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ Telegram token або chat_id не встановлені")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, data=data)
        if response.status_code != 200:
            print(f"❌ Telegram помилка: {response.text}")
        else:
            print("✅ Повідомлення надіслано в Telegram")
    except Exception as e:
        print(f"❌ Помилка надсилання в Telegram: {e}")
