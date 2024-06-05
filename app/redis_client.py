import redis
from app.core.config import Settings


settings = Settings(_env_file='../.env')
r = redis.Redis(host=settings.redis_host, port=6379, db=0)
# r = redis.Redis(host='localhost', port=6379, db=0)
