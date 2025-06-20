from db_config import get_db_engine
from langchain_community.utilities.sql_database import SQLDatabase

if __name__ == "__main__":
    print("Testing MySQL database connection...")
    try:
        engine = get_db_engine()
        db = SQLDatabase(engine)
        tables = db.get_usable_table_names()
        print("Connection successful!")
        print(f"Tables in the database: {tables}")
    except Exception as e:
        print("Connection failed:", e) 