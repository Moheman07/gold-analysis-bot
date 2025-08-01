import yfinance as yf
import json

OUTPUT_FILENAME = "yield_data.json"

print("--> جاري سحب بيانات عائدات السندات...")
# الرمز الخاص بعائدات سندات الخزانة لأجل 10 سنوات
tnx = yf.Ticker("^TNX")

# جلب بيانات آخر يوم
hist = tnx.history(period="1d")

if hist.empty:
    print("!!! فشل في سحب بيانات العائدات.")
else:
    latest_yield = hist['Close'].iloc[-1]
    output = {
        "yield_10y": round(latest_yield, 2)
    }

    with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

    print(f"... تم حفظ بيانات العائدات بنجاح في ملف {OUTPUT_FILENAME}")
