import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load environment variables from .env file
def load_env():
    load_dotenv()

# Get SQLAlchemy engine for MySQL
def get_db_engine():
    load_env()
    user = os.getenv("MYSQL_USER")
    password = os.getenv("MYSQL_PASSWORD")
    host = os.getenv("MYSQL_HOST", "localhost")
    port = os.getenv("MYSQL_PORT", "3306")
    db = os.getenv("MYSQL_DB")
    conn_str = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{db}"
    return create_engine(conn_str)

# Get OpenAI API key
def get_openai_api_key():
    load_env()
    return os.getenv("OPENAI_API_KEY") 