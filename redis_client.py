import redis
import logging
from config import Settings

# 创建日志记录器
logger = logging.getLogger("custom_logger")
logger.setLevel(logging.INFO)

settings = Settings(_env_file='.env')
logger.debug(f"settings redis_host: {settings.redis_host}")
r = redis.Redis(host=settings.redis_host, port=6379, db=0)
# r = redis.Redis(host='localhost', port=6379, db=0)
