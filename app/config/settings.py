from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App
    APP_NAME: str = "NoaVoiceAI"
    DEBUG: bool = False
    
    # Cal.com V2
    CALCOM_API_KEY: str
    CALCOM_EVENT_TYPE_ID: int
    CALCOM_BASE_URL: str = "https://api.cal.com/v2"
    CALCOM_API_VERSION: str = "2024-08-13"
    CALCOM_TIMEOUT: int = 30
    
    # Neon PostgreSQL
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str 
    EXPIRE_IN_TIME: int

    OPENAI_API_KEY: str

    #google login credentials
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str

    ELEVEN_LABS_API_KEY: str
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    BASE_DOMAIN: str = ""
    BASE_URL: str = ""

# Single instance used everywhere
settings = Settings()