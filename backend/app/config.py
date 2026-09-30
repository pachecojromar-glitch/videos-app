from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "sqlite:///./local.db"
    secret_key: str = "cambiar-en-produccion"
    algorithm: str = "HS256"
    access_token_minutes: int = 60

    storage_backend: str = "local"          # "local" o "s3"
    public_base_url: str = "http://127.0.0.1:8000"
    media_dir: str = "media"

    aws_region: str = "us-east-1"
    s3_videos_bucket: str = "pacheco-videoapp-videos1"
    s3_thumbnails_bucket: str = "pacheco-videoapp-thumbnails"

    max_video_mb: int = 100
    max_thumbnail_mb: int = 5

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
