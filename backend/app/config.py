from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "sqlite:///./local.db"
    secret_key: str = "cambiar-en-produccion"
    algorithm: str = "HS256"
    access_token_minutes: int = 60

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
