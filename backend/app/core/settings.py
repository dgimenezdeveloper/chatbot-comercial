from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Base de datos
    DATABASE_URL: str
    POSTGRES_USER: str = "chatbot"
    POSTGRES_PASSWORD: str = "chatbot123"
    POSTGRES_DB: str = "chatbot_db"

    # Redis
    REDIS_URL: str

    # Seguridad
    SECRET_KEY: str

    # WhatsApp Business API
    WHATSAPP_TOKEN: str
    WHATSAPP_VERIFY_TOKEN: str
    WHATSAPP_PHONE_NUMBER_ID: str
    WHATSAPP_BUSINESS_ACCOUNT_ID: str
    META_API_VERSION: str = "v25.0"

    # Google Calendar API
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str
    GOOGLE_CALENDAR_ID: str = "primary"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Entorno de la aplicación
    APP_ENV: str = "development"

settings = Settings()
