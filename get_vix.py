import yfinance as yf
import json

OUTPUT_FILENAME = "vix_data.json"

print("--> جاري سحب بيانات مؤشر VIX...")
# الرمز الخاص بمؤشر VIX في ياهو فاينانس
vix = yf.Ticker("^VIX")

# جلب بيانات آخر يوم
hist = vix.history(period="1d")

if hist.empty:
    print("!!! فشل في سحب بيانات VIX.")
else:
    latest_price = hist['Close'].iloc[-1]
    output = {
        "vix_price": round(latest_price, 2)
    }

    with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

    print(f"... تم حفظ بيانات VIX بنجاح في ملف {OUTPUT_FILENAME}")
