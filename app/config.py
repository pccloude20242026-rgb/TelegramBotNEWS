from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Telegram
    bot_token: str
    channel_id: str  # masalan: @mening_kanalim yoki -1001234567890

    # Twelve Data (oltin, kumush, neft, USD/UZS uchun)
    twelvedata_api_key: str = ""

    # Yangilanish intervallari (soniyada)
    price_update_interval: int = 120       # 2 daqiqa (1-5 daqiqa oralig'ida)
    news_check_interval: int = 300         # 5 daqiqa

    # Faqat "High" va "Medium" impactli yangiliklarni yuborish
    min_news_impact: str = "Medium"        # Low / Medium / High

    # Narxlar postini alohida xabar sifatida qancha vaqtda 1 marta yuborish
    # (har safar narx yangilansa emas, spam bo'lmasligi uchun)
    price_post_every_n_updates: int = 1


settings = Settings()
