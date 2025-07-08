import math
from telegram_bot import send_telegram_message
from utils import format_price

def check_long_short_signal(results, symbol):
    data_5m = results['5m']
    data_15m = results['15m']

    # Простий підрахунок ймовірностей
    long_score = 0
    short_score = 0
    total_checks = 6

    if data_5m['rsi'] > 70 and data_15m['rsi'] > 60:
        long_score += 1
    elif data_5m['rsi'] < 30 and data_15m['rsi'] < 40:
        short_score += 1

    if data_5m['macd'] > data_5m['macd_signal'] and data_15m['macd'] > data_15m['macd_signal']:
        long_score += 1
    elif data_5m['macd'] < data_5m['macd_signal'] and data_15m['macd'] < data_15m['macd_signal']:
        short_score += 1

    if data_5m['stoch_k'] > 80 and data_5m['stoch_d'] > 80:
        long_score += 1
    elif data_5m['stoch_k'] < 20 and data_5m['stoch_d'] < 20:
        short_score += 1

    if data_5m['ema50'] > data_5m['ema200']:
        long_score += 1
    else:
        short_score += 1

    if data_5m['direction'] == 'up':
        long_score += 1
    else:
        short_score += 1

    if data_5m['volume_ok'] and data_15m['volume_ok']:
        long_score += 1
        short_score += 1

    long_prob = round((long_score / total_checks) * 100)
    short_prob = round((short_score / total_checks) * 100)

    print(f"📊 Ймовірність ЛОНГУ: {long_prob}% | ШОРТУ: {short_prob}%")

    # ✅ Кастомна умова: напрямок + обʼєм + >70%
    if (
        short_prob > 70 and
        data_5m['volume_ok'] and data_15m['volume_ok'] and
        data_5m['direction'] == 'down' and data_15m['direction'] == 'down'
    ):
        direction = "ШОРТ"
        prob = short_prob
    elif (
        long_prob > 70 and
        data_5m['volume_ok'] and data_15m['volume_ok'] and
        data_5m['direction'] == 'up' and data_15m['direction'] == 'up'
    ):
        direction = "ЛОНГ"
        prob = long_prob
    # 🟡 Якщо кастомна умова не спрацювала — fallback на стару умову
    elif max(long_prob, short_prob) >= 80:
        direction = "ЛОНГ" if long_prob > short_prob else "ШОРТ"
        prob = max(long_prob, short_prob)
    else:
        print("⚪ Сигнал не підтверджено — недостатня впевненість")
        return

    price = data_5m['price']
    if direction == "ЛОНГ":
        tp1 = price + data_5m['atr']
        tp2 = price + (data_5m['ema200'] - price) * 0.9
        tp3 = data_5m['bb_upper']
    else:
        tp1 = price - data_5m['atr']
        tp2 = price - (price - data_5m['ema200']) * 0.9
        tp3 = data_5m['bb_lower']

    tp = (tp1 + tp2 + tp3) / 3

    msg = f"{'🟢' if direction == 'ЛОНГ' else '🔴'} За 5 хвилин ймовірно буде сигнал на {direction} по {symbol.upper()} (ймовірність: {prob}%)\n"
    msg += f"\nЦіна: {format_price(price)}\n"
    msg += f"🎯 Тейк-профіт (середній): {format_price(tp)}"

    send_telegram_message(msg)
