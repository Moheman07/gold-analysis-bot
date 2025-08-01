import yfinance as yf
import pandas_ta as ta
import requests
import json
import os

# --- 1. الإعدادات ---
GOLD_TICKER = "GC=F"
# سنقرأ الرابط من الـ Secrets لاحقاً
N8N_WEBHOOK_URL = os.environ.get("N8N_WEBHOOK_URL")

# --- 2. سحب البيانات ---
print("--> الخطوة 1: جاري سحب بيانات الذهب...")
data = yf.download(GOLD_TICKER, period="250d", interval="1d")

# إصلاح هيكل الأعمدة
data.columns = data.columns.droplevel(1)

if data.empty:
    print("!!! فشل في سحب البيانات.")
elif N8N_WEBHOOK_URL is None:
    print("!!! خطأ: لم يتم العثور على رابط الويبهوك في الـ Secrets.")
else:
    print("... نجح سحب البيانات!")

    # --- 3. حساب المؤشرات الفنية ---
    print("--> الخطوة 2: جاري حساب المؤشرات الفنية...")
    data.ta.sma(length=50, append=True)
    data.ta.sma(length=200, append=True)
    data.ta.rsi(length=14, append=True)
    data.ta.macd(append=True)
    data.ta.bbands(append=True)
    print("... تم حساب المؤشرات.")

    # --- 4. توليد الإشارة النهائية ---
    print("--> الخطوة 3: جاري توليد إشارة التداول النهائية...")
    latest_data = data.iloc[-1]

    price = latest_data['Close']
    sma200 = latest_data['SMA_200']
    rsi = latest_data['RSI_14']
    macd_line = latest_data['MACD_12_26_9']
    macd_signal_line = latest_data['MACDs_12_26_9']

    is_long_term_uptrend = price > sma200
    is_macd_bullish = macd_line > macd_signal_line

    signal = "Neutral"
    if is_long_term_uptrend and is_macd_bullish and rsi > 52:
        signal = "Strong Buy"
    elif is_long_term_uptrend and is_macd_bullish:
        signal = "Buy"
    elif not is_long_term_uptrend and not is_macd_bullish and rsi < 48:
        signal = "Strong Sell"
    elif not is_long_term_uptrend and not is_macd_bullish:
        signal = "Sell"

    # --- 5. تجهيز وإرسال البيانات إلى n8n ---
    output_data = {
        "asset": "الذهب (XAU/USD)",
        "price": round(price, 2),
        "technical_analysis": {
            "signal": signal,
            "rsi_14": round(rsi, 2),
            "sma_200": round(sma200, 2),
            "macd_line": round(macd_line, 2),
            "macd_signal": round(macd_signal_line, 2)
        }
    }

    print("--> الخطوة 4: جاري إرسال البيانات إلى n8n...")
    try:
        response = requests.post(N8N_WEBHOOK_URL, json=output_data)
        response.raise_for_status()
        print("... تم إرسال البيانات بنجاح إلى n8n!")
    except requests.exceptions.RequestException as e:
        print(f"!!! حدث خطأ أثناء إرسال البيانات إلى n8n: {e}")
