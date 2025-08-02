import yfinance as yf
import pandas_ta as ta
import json

# --- 1. الإعدادات ---
GOLD_TICKER = "GC=F"
OUTPUT_FILENAME = "analysis.json"
ATR_MULTIPLIER_SL = 2.0  # مضاعف ATR لوقف الخسارة
RISK_REWARD_RATIO = 1.5  # نسبة المخاطرة إلى العائد

# --- 2. سحب البيانات ---
print("--> الخطوة 1: جاري سحب بيانات الذهب...")
data = yf.download(GOLD_TICKER, period="260d", interval="1d", auto_adjust=False)
data.columns = [col[0].lower() for col in data.columns]

if data.empty:
    print("!!! فشل في سحب البيانات.")
else:
    print("... نجح سحب البيانات!")

    # --- 3. حساب المؤشرات الفنية ---
    print("--> الخطوة 2: جاري حساب المؤشرات الفنية...")
    custom_analysis = ta.Strategy(
        name="Custom Strategy",
        ta=[
            {"kind": "sma", "length": 50},
            {"kind": "sma", "length": 200},
            {"kind": "rsi"},
            {"kind": "macd"},
            {"kind": "bbands"},
            {"kind": "atr"},
            {"kind": "obv"}
        ]
    )
    data.ta.strategy(custom_analysis)
    data['OBV_SMA_20'] = ta.sma(data['OBV'], length=20)
    print("... تم حساب المؤشرات.")

    # --- 4. توليد الإشارة النهائية ---
    print("--> الخطوة 3: جاري توليد إشارة التداول النهائية...")
    latest_data = data.iloc[-1]

    price = latest_data['close']
    sma200 = latest_data['SMA_200']
    rsi = latest_data['RSI_14']
    macd_line = latest_data['MACD_12_26_9']
    macd_signal_line = latest_data['MACDs_12_26_9']
    atr = latest_data['ATRr_14']

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

    # --- 5. حساب مستويات إدارة المخاطر ---
    stop_loss = None
    take_profit = None
    if "Buy" in signal:
        stop_loss = price - (atr * ATR_MULTIPLIER_SL)
        take_profit = price + ((price - stop_loss) * RISK_REWARD_RATIO)
    elif "Sell" in signal:
        stop_loss = price + (atr * ATR_MULTIPLIER_SL)
        take_profit = price - ((stop_loss - price) * RISK_REWARD_RATIO)

    # --- 6. تجهيز البيانات للحفظ ---
    output_data = {
        "asset": "الذهب (XAU/USD)",
        "price": round(price, 2),
        "technical_analysis": {
            "signal": signal,
            "rsi_14": round(rsi, 2),
            "sma_200": round(sma200, 2),
            "macd_line": round(macd_line, 2),
            "macd_signal": round(macd_signal_line, 2),
            "atr": round(atr, 2),
            "obv_signal": "positive" if latest_data['OBV'] > latest_data['OBV_SMA_20'] else "negative"
        },
        "risk_management": {
            "stop_loss": round(stop_loss, 2) if stop_loss is not None else "N/A",
            "take_profit": round(take_profit, 2) if take_profit is not None else "N/A"
        }
    }

    # --- 7. حفظ المخرجات في ملف ---
    with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)

    print(f"--> الخطوة 4: تم حفظ التحليل بنجاح في ملف {OUTPUT_FILENAME}")
