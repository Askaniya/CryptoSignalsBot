from ta.momentum import RSIIndicator, StochasticOscillator
from ta.trend import MACD, EMAIndicator
from ta.volatility import BollingerBands, AverageTrueRange
from utils import get_klines, format_price
from signal_logic import check_long_short_signal
from config import VOLUME_MULTIPLIER
from binance_config import client

def analyze_pair(symbol):
    timeframes = ['5m', '15m']
    results = {}

    for tf in timeframes:
        df = get_klines(symbol, tf)

        if df.empty or len(df) < 50:
            print(f"⚠️ Недостатньо даних по {symbol.upper()} ({tf}) — пропускаю")
            return

        close, high, low, volume = df['close'], df['high'], df['low'], df['volume']

        rsi = RSIIndicator(close, window=14).rsi().iloc[-1]
        macd_ind = MACD(close)
        macd = macd_ind.macd().iloc[-1]
        macd_signal = macd_ind.macd_signal().iloc[-1]
        ema50 = EMAIndicator(close, window=50).ema_indicator().iloc[-1]
        ema200 = EMAIndicator(close, window=200).ema_indicator().iloc[-1]
        stoch = StochasticOscillator(high=high, low=low, close=close)
        stoch_k = stoch.stoch().iloc[-1]
        stoch_d = stoch.stoch_signal().iloc[-1]
        bb = BollingerBands(close)
        bb_lower = bb.bollinger_lband().iloc[-1]
        bb_upper = bb.bollinger_hband().iloc[-1]
        atr = AverageTrueRange(high=high, low=low, close=close, window=14).average_true_range().iloc[-1]
        last_volume = volume.iloc[-1]
        avg_volume = volume[-20:].mean()

        try:
            live_price = float(client.get_symbol_ticker(symbol=symbol.upper())["price"])
        except Exception as e:
            print(f"❌ Помилка отримання живої ціни {symbol.upper()}: {e}")
            live_price = close.iloc[-1]  # fallback

        direction = "up" if live_price > close.iloc[-2] else "down"
        volume_ok = last_volume > avg_volume * VOLUME_MULTIPLIER

        results[tf] = {
            'price': live_price,
            'rsi': rsi,
            'macd': macd,
            'macd_signal': macd_signal,
            'ema50': ema50,
            'ema200': ema200,
            'stoch_k': stoch_k,
            'stoch_d': stoch_d,
            'bb_lower': bb_lower,
            'bb_upper': bb_upper,
            'atr': atr,
            'volume': last_volume,
            'avg_volume': avg_volume,
            'volume_ok': volume_ok,
            'direction': direction
        }

        output = f"{symbol.upper()} | {tf} | Ціна: {format_price(live_price)} | RSI: {rsi:.1f} | MACD: {macd:.2f} | "
        output += f"ST_K: {stoch_k:.1f} | ST_D: {stoch_d:.1f} | BB: {format_price(bb_lower)}-{format_price(bb_upper)} | "
        output += f"Обʼєм: {last_volume:.1f} | OK: {volume_ok} | EMA50>EMA200: {ema50 > ema200} | Напрям: {direction}"
        print(output)

    check_long_short_signal(results, symbol)
