from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    redis_host: str = 'localhost'
    redis_port: int = 6379
    redis_db: int = 0

    # database_username: str = 'myuser'
    # database_password: str = 'mypassword'


