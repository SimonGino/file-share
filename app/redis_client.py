import redis
from app.core.config import get_settings

# Load settings from environment file
settings=get_settings()

r = redis.Redis(host=settings.redis_host, port=settings.redis_port, db=settings.redis_db)
# r = redis.Redis(host='localhost', port=6379, db=0)
