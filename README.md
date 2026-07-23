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
3. Neft narxi kerak bo'lsa, https://www.oilpriceapi.com/ da bepul (kartasiz)
   ro'yxatdan o'tib API key oling. Oltin/Kumush/BTC/USD-UZS uchun **hech
   qanday key kerak emas**.

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

## Ma'lumot manbalari (barchasi bepul)

| Aktiv | Manba | Key kerakmi? | Cheklov |
|---|---|---|---|
| Oltin (XAU), Kumush (XAG) | [gold-api.com](https://gold-api.com) | Yo'q | Cheklovsiz (30s keshlash tavsiya etiladi) |
| BTC | Binance public API | Yo'q | Amalda cheklovsiz |
| Neft (WTI) | [oilpriceapi.com](https://www.oilpriceapi.com) | Ha (bepul, kartasiz) | ~200 so'rov/oy |
| USD/UZS | [cbu.uz](https://cbu.uz) — O'zbekiston Markaziy banki rasmiy API'si | Yo'q | Kunlik yangilanadi |
| Yangiliklar | ForexFactory JSON kalendar feedi | Yo'q | — |

## Muhim eslatmalar

- **Neft va USD/UZS narxlari** rasmiy manbalar bo'lgani uchun kamdan-kam
  (standart holatda har 4 soatda) yangilanadi — buni tez-tez so'rashning
  ma'nosi yo'q, chunki qiymat kuniga bir necha marta yoki hatto bir marta
  o'zgaradi. Oltin/Kumush/BTC esa cheklovsiz manba bo'lgani uchun har
  1-5 daqiqada yangilanadi.
- **Neft narxi**: agar `.env`da `OILPRICEAPI_KEY` bo'sh qolsa, bot bu
  qiymatni "⚠️ ma'lumot yo'q" deb ko'rsatadi — ixtiyoriy, lekin xohlasangiz
  qo'shishingiz mumkin.
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
