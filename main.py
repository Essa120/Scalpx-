import requests
import time
import os
import logging
from datetime import datetime
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()

# إعدادات البوت
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
bot = Bot(token=BOT_TOKEN)

# أدوات المراقبة
ASSETS = {
    "GOLD": "XAU/USD",
    "BTC-USD": "BTC/USD",
    "ETH-USD": "ETH/USD",
    "US30": "DJI",
    "US100": "NDX"
}

API_URL = "https://api.twelvedata.com/time_series"
API_KEY = os.getenv("OPENAI_API_KEY")
INTERVAL = "5min"

sent_signals = {}

# دالة الحصول على البيانات
def get_price(symbol):
    try:
        response = requests.get(API_URL, params={
            "symbol": symbol,
            "interval": INTERVAL,
            "apikey": API_KEY,
            "outputsize": 2
        })
        data = response.json()
        values = data.get("values")
        if values:
            return float(values[0]["close"]), float(values[1]["close"])
        else:
            return None, None
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None, None

# دالة تحليل التقاطع
def check_crossover(current, previous):
    if current > previous:
        return "BUY"
    elif current < previous:
        return "SELL"
    return None

# إرسال الإشعار
def send_signal(asset, action, price):
    msg = f"إشارة {action} على {asset} @ {price}"
    if sent_signals.get(asset) != msg:
        bot.send_message(chat_id=CHAT_ID, text=msg)
        sent_signals[asset] = msg

# تشغيل السكربت
def run_bot():
    for name, symbol in ASSETS.items():
        current, previous = get_price(symbol)
        if current and previous:
            signal = check_crossover(current, previous)
            if signal:
                send_signal(name, signal, current)

if __name__ == "__main__":
    while True:
        try:
            run_bot()
            time.sleep(300)  # كل 5 دقائق
        except Exception as e:
            bot.send_message(chat_id=CHAT_ID, text=f"حدث خطأ: {e}")
            time.sleep(60)
