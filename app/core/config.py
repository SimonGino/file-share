from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    redis_host: str = 'localhost'
    redis_port: int = 6379
    redis_db: int = 0
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str = "root"
    mysql_password: str = "root"
    mysql_db: str = ""

    class Config:
        env_prefix = ''
        env_file = "app/.env"
        env_file_encoding = 'utf-8'

# settings = Settings()

@lru_cache
def get_settings():
    return Settings()