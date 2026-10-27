import os
import time
import asyncio
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from telegram import Bot

# Mengambil Token dan Chat ID dari Environment Variables (Nanti diatur di Railway)
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Instrumen Trading
SYMBOLS = {
    "Nasdaq (US100)": "NQ=F",
    "XAU/USD": "XAUUSD=X",
    "USD/JPY": "JPY=X"
}

async def send_alert(bot, message):
    try:
        await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")
    except Exception as e:
        print(f"Gagal mengirim pesan: {e}")

def analyze_market(symbol, ticker):
    # Mengambil data 15 menit
    df = yf.download(ticker, period="5d", interval="15m", progress=False)
    if df.empty or len(df) < 20:
        return None
        
    # Perbaikan format tabel yfinance terbaru
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)

    # Indikator teknikal (RSI & EMA) untuk filter tren
    df.ta.rsi(length=14, append=True)
    df.ta.ema(length=20, append=True)
    
    last = df.iloc[-1]
    rsi = last.get('RSI_14', 50)
    ema = last.get('EMA_20', 0)
    close = last['Close']

    # Logika sinyal (Bisa disesuaikan lebih lanjut dengan konsep ICT/FVG)
    if rsi < 30 and close > ema:
        return f"🟢 *BULLISH SIGNAL* | {symbol}\nHarga menembus EMA20 dari area Oversold.\n*Harga:* {close:.2f}\n*RSI:* {rsi:.2f}"
    elif rsi > 70 and close < ema:
        return f"🔴 *BEARISH SIGNAL* | {symbol}\nHarga di bawah EMA20 dari area Overbought.\n*Harga:* {close:.2f}\n*RSI:* {rsi:.2f}"
    
    return None

async def main():
    if not TOKEN or not CHAT_ID:
        print("Error: TELEGRAM_TOKEN atau TELEGRAM_CHAT_ID belum diatur!")
        return

    bot = Bot(token=TOKEN)
    await send_alert(bot, "🤖 *Bot ICT Trading Aktif*\nSistem berjalan 24/7 di Railway memantau Nasdaq, XAUUSD, dan USDJPY.")

    while True:
        for name, ticker in SYMBOLS.items():
            try:
                signal = analyze_market(name, ticker)
                if signal:
                    await send_alert(bot, signal)
            except Exception as e:
                print(f"Error pada {name}: {e}")
        
        # Jeda 15 menit sebelum analisis ulang
        time.sleep(900)

if __name__ == "__main__":
    asyncio.run(main())
