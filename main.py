import requests
import pandas as pd
import time
import os
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=payload)

def fetch_gold_data():
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": "XAUUSD",
        "interval": "15min",
        "apikey": os.environ.get("ALPHA_VANTAGE_KEY")
    }
    response = requests.get(url, params=params)
    data = response.json()
    prices = data.get("Time Series (15min)", {})
    df = pd.DataFrame.from_dict(prices, orient="index")
    df = df.rename(columns={
        "1. open": "open",
        "2. high": "high",
        "3. low": "low",
        "4. close": "close",
        "5. volume": "volume"
    })
    df = df.astype(float)
    df.sort_index(inplace=True)
    return df

def analyze_and_notify(df):
    df["rsi"] = RSIIndicator(close=df["close"], window=14).rsi()
    df["sma"] = SMAIndicator(close=df["close"], window=20).sma_indicator()

    latest = df.iloc[-1]
    previous = df.iloc[-2]

    if latest["rsi"] < 30 and latest["close"] > latest["sma"] and previous["close"] < previous["sma"]:
        send_telegram_message("ð Buy Signal for Gold!")
    elif latest["rsi"] > 70 and latest["close"] < latest["sma"] and previous["close"] > previous["sma"]:
        send_telegram_message("ð Sell Signal for Gold!")
    else:
        print("No signal")

if __name__ == "__main__":
    try:
        df = fetch_gold_data()
        analyze_and_notify(df)
    except Exception as e:
        send_telegram_message(f"â ï¸ Error: {e}")
