from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Telegram
    bot_token: str
    channel_id: str  # masalan: @mening_kanalim yoki -1001234567890

    # OilPriceAPI.com — bepul reja (kartasiz), lekin oyiga cheklangan so'rov
    # (odatda ~200/oy). https://www.oilpriceapi.com/ dan bepul ro'yxatdan o'ting.
    oilpriceapi_key: str = ""

    # Yangilanish intervallari (soniyada)
    # Oltin/Kumush/BTC — cheklovsiz manba, shuning uchun tez-tez so'rasa bo'ladi
    fast_price_update_interval: int = 120      # 2 daqiqa (1-5 daqiqa oralig'ida)
    # Neft/USD-UZS — cheklangan/kunlik manba, kamroq so'raladi
    slow_price_update_interval: int = 14400    # 4 soatda bir marta
    news_check_interval: int = 300             # 5 daqiqa

    # Faqat "High" va "Medium" impactli yangiliklarni yuborish
    min_news_impact: str = "Medium"        # Low / Medium / High

    # Narxlar postini alohida xabar sifatida qancha vaqtda 1 marta yuborish
    # (har safar narx yangilansa emas, spam bo'lmasligi uchun)
    price_post_every_n_updates: int = 1


settings = Settings()
