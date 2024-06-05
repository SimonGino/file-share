from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import get_settings
import logging

# 配置日志记录器
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load settings from environment file
settings=get_settings()

# Read database configuration from environment variables
mysql_host = settings.mysql_host
mysql_port = settings.mysql_port
mysql_user = settings.mysql_user
mysql_password = settings.mysql_password
mysql_db = settings.mysql_db

# Default to SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
connect_args = {"check_same_thread": False}

# If MySQL configuration is provided, attempt to use MySQL
if mysql_host and mysql_port and mysql_user and mysql_password and mysql_db:
    mysql_url = f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_db}"
    logger.info("mysql url: {}".format(mysql_url))
    try:
        # Test MySQL connection
        test_engine = create_engine(mysql_url)
        test_connection = test_engine.connect()
        test_connection.close()
        SQLALCHEMY_DATABASE_URL = mysql_url
        connect_args = {}  # No need for specific connect_args for MySQL
    except OperationalError as e:
        print(f"Failed to connect to MySQL: {e}")
        print("Falling back to SQLite.")

# Create the engine with the appropriate database URL and connection arguments
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
