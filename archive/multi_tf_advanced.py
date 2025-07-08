from binance_config import client
import pandas as pd
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.trend import MACD, EMAIndicator
from ta.volatility import BollingerBands

def get_klines(symbol, interval='5m', limit=250):
    raw = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    df = pd.DataFrame(raw, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_vol', 'taker_buy_quote_vol', 'ignore'
    ])
    df['close'] = df['close'].astype(float)
    df['high'] = df['high'].astype(float)
    df['low'] = df['low'].astype(float)
    df['time'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

def analyze(symbol):
    timeframes = ['5m', '15m']
    results = {}

    for tf in timeframes:
        df = get_klines(symbol, tf)
        close = df['close']
        high = df['high']
        low = df['low']

        # Індикатори
        rsi = RSIIndicator(close, window=14).rsi().iloc[-1]
        macd_ind = MACD(close)
        macd = macd_ind.macd().iloc[-1]
        macd_signal = macd_ind.macd_signal().iloc[-1]
        ema50 = EMAIndicator(close, window=50).ema_indicator().iloc[-1]
        ema200 = EMAIndicator(close, window=200).ema_indicator().iloc[-1]
        stoch = StochasticOscillator(high=high, low=low, close=close, window=14, smooth_window=3)
        stoch_k = stoch.stoch().iloc[-1]
        stoch_d = stoch.stoch_signal().iloc[-1]
        bb = BollingerBands(close, window=20, window_dev=2)
        bb_lower = bb.bollinger_lband().iloc[-1]
        bb_upper = bb.bollinger_hband().iloc[-1]
        price = close.iloc[-1]
        direction = "up" if close.iloc[-1] > close.iloc[-2] else "down"

        results[tf] = {
            'price': price,
            'rsi': rsi,
            'macd': macd,
            'macd_signal': macd_signal,
            'ema50': ema50,
            'ema200': ema200,
            'stoch_k': stoch_k,
            'stoch_d': stoch_d,
            'bb_lower': bb_lower,
            'bb_upper': bb_upper,
            'direction': direction
        }

        print(f"{symbol} | {tf} | Ціна: {price:.2f} | RSI: {rsi:.1f} | MACD: {macd:.2f} | ST_K: {stoch_k:.1f} | ST_D: {stoch_d:.1f} | BB нижня: {bb_lower:.2f} | верхня: {bb_upper:.2f} | EMA50>EMA200: {ema50 > ema200} | Напрям: {direction}")

    # Об’єднана логіка
    r5, r15 = results['5m'], results['15m']

    long_signal = (
        r5['rsi'] < 35 and r15['rsi'] < 35 and
        r5['macd'] > r5['macd_signal'] and r15['macd'] > r15['macd_signal'] and
        r5['stoch_k'] > r5['stoch_d'] and r5['stoch_k'] < 20 and
        r5['price'] < r5['bb_lower'] and
        r5['ema50'] > r5['ema200'] and r15['ema50'] > r15['ema200']
    )

    short_signal = (
        r5['rsi'] > 65 and r15['rsi'] > 65 and
        r5['macd'] < r5['macd_signal'] and r15['macd'] < r15['macd_signal'] and
        r5['stoch_k'] < r5['stoch_d'] and r5['stoch_k'] > 80 and
        r5['price'] > r5['bb_upper'] and
        r5['ema50'] < r5['ema200'] and r15['ema50'] < r15['ema200']
    )

    if long_signal:
        print("🟢 СИЛЬНИЙ СИГНАЛ НА ЛОНГ (усі умови виконано)")
    elif short_signal:
        print("🔴 СИЛЬНИЙ СИГНАЛ НА ШОРТ (усі умови виконано)")
    else:
        print("⚪ Немає чіткого сигналу — часткове співпадіння або суперечності")

if __name__ == "__main__":
    analyze("BTCUSDT")
