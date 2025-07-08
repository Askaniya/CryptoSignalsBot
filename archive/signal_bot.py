from binance_config import client

def get_price(symbol):
    try:
        ticker = client.get_symbol_ticker(symbol=symbol)
        return float(ticker["price"])
    except Exception as e:
        print(f"Помилка: {e}")
        return None

if __name__ == "__main__":
    symbol = "BTCUSDT"
    price = get_price(symbol)
    if price:
        print(f"Ціна {symbol}: {price} USD")
