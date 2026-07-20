# Forex News Bot (O'zbek tilida)

ForexFactory kalendaridan muhim iqtisodiy yangiliklarni va Oltin/Kumush/Neft/
USD-UZS/BTC narxlarini avtomatik ravishda Telegram kanaliga yuboradigan bot.

## Ishga tushirish

```bash
python -m venv venv
source venv/bin/activate  # Windowsda: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# .env faylini to'ldiring: BOT_TOKEN, CHANNEL_ID, TWELVEDATA_API_KEY

python main.py
```

Bot ishga tushishidan oldin:
1. @BotFather orqali bot yarating va tokenni oling
2. Botni kanalingizga **admin** qilib qo'shing (xabar yuborish huquqi bilan)
3. https://twelvedata.com/ da ro'yxatdan o'tib bepul API key oling

## Railway'ga deploy qilish

1. Ushbu papkani GitHub repo qiling
2. Railway'da "New Project" → "Deploy from GitHub repo"
3. Railway avtomatik `Procfile`ni topib, `worker` processini ishga tushiradi
4. Railway loyihasining "Variables" bo'limiga `.env.example`dagi barcha
   o'zgaruvchilarni qo'shing

## Fayl tuzilishi

```
app/
  config.py         # sozlamalar (.env dan o'qiydi)
  news_source.py     # ForexFactory JSON kalendar feedi
  price_source.py    # Twelve Data + Binance narxlar
  formatter.py        # Telegram uchun O'zbek tilidagi matn formatlash
  bot.py               # asosiy scheduler + botning ishga tushishi
main.py
```

## Muhim eslatmalar

- **Neft narxi (WTI)**: Twelve Data'ning bepul planida ba'zan mavjud
  bo'lmasligi mumkin. Agar `⚠️ ma'lumot yo'q` chiqsa, pullik planga
  o'tish yoki boshqa manba (masalan EIA API) ulash kerak bo'ladi.
- **ForexFactory feed**: `nfs.faireconomy.media` — bu rasmiy bo'lmagan,
  lekin ko'plab trading botlar tomonidan ishlatiladigan barqaror manba.
  Agar u ishlamay qolsa, `app/news_source.py` faylida shunga o'xshash
  interfeys bilan boshqa manbaga (Investing.com RSS va h.k.) almashtirish
  mumkin.
- **Narx o'zgarish belgilari** (⬆️⬇️➡️) oldingi yuborilgan narx bilan
  solishtirib chiqariladi, `state.json` faylida saqlanadi.
- Xabarlar spam bo'lib ketmasligi uchun yangiliklar faqat "Medium" va undan
  yuqori impact darajasida, va faqat natija (`actual`) e'lon qilingandan
  keyin yuboriladi.

## Kengaytirish g'oyalari

- `/narxlar` va `/bugungi_yangiliklar` kabi buyruqlar qo'shish (on-demand)
- Claude/GPT orqali yangilikni yanada "jonli" tahlil bilan boyitish
- Obuna tizimi (Click/Payme) bilan premium kanal — signal ilovangizga
  o'xshab
