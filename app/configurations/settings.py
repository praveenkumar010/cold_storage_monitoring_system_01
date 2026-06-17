<<<<<<< HEAD
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict
)

class Settings(BaseSettings):

=======
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
>>>>>>> 3f520bf8a46d120c73bdcb525ad2cfdfc93d9990
    DB_USER: str = "root"
    DB_PASSWORD: str = "password"
    DB_HOST: str = "localhost"
    DB_NAME: str = "cold_storage"

    APP_NAME: str = "Cold Storage Monitoring System"
    DEBUG: bool = True

<<<<<<< HEAD
=======

>>>>>>> 3f520bf8a46d120c73bdcb525ad2cfdfc93d9990
    @property
    def DATABASE_URL(self):
        return "sqlite:///./test.db"

<<<<<<< HEAD
    model_config = SettingsConfigDict(
        env_file=".env"
    )

settings = Settings()
=======
    class Config:
        env_file = ".env"   

settings = Settings()
>>>>>>> 3f520bf8a46d120c73bdcb525ad2cfdfc93d9990
