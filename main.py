import time
from datetime import datetime
from analyzer import analyze_pair
from config import SYMBOLS

def run_analysis():
    print(f"\n⏱ Запуск аналізу: {datetime.now().strftime('%H:%M:%S')}")
    for symbol in SYMBOLS:
        analyze_pair(symbol)

print("🚀 Бот запущено. Очікування найближчої свічки...")

while True:
    now = datetime.now()
    if now.minute % 5 == 0 and now.second == 10:
        run_analysis()
        time.sleep(60)  # щоб не повторювало того ж самого разу
    else:
        time.sleep(1)
