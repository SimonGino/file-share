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

    MINIO_ROOT_USER: str = "admin"
    MINIO_ROOT_PASSWORD: str = "1122qazwsx"
    MINIO_HOST: str = "localhost"
    MINIO_PORT: int = 9000
    MINIO_SECURE: bool = False
    MINIO_BUCKET_NAME: str = "minio-bucket"
    MINIO_URI: str = ""

    OPENAI_API_KEY: str = ""
    OPENAI_API_BASE_URL: str = ""


    class Config:
        env_file = ".env"


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()