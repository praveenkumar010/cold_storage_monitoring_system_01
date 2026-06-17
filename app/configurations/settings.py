from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    DB_USER: str = "root"
    DB_PASSWORD: str = "password"
    DB_HOST: str = "localhost"
    DB_NAME: str = "cold_storage"

    APP_NAME: str = "Cold Storage Monitoring System"
    DEBUG: bool = True

    @property
    def DATABASE_URL(self) -> str:
        return "sqlite:///./test.db"

    model_config = SettingsConfigDict(
        env_file=".env"
    )

settings = Settings()