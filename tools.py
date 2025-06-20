from langchain_community.utilities.sql_database import SQLDatabase
from sqlalchemy import create_engine
import os

# Run a query safely, return result or error message
def safe_query(db: SQLDatabase, query: str):
    try:
        result = db.run(query)
        return result
    except Exception as e:
        return f"Error: {e}"

# List all tables in the database (placeholder)
def list_tables(db: SQLDatabase):
    return db.get_usable_table_names()

# Get schema for a table (placeholder)
def get_schema(db: SQLDatabase, table: str):
    return db.get_table_info(table)

# List all databases
def list_databases(db: SQLDatabase):
    try:
        # This works for MySQL
        result = db.run("SHOW DATABASES;")
        return [row[0] for row in result]
    except Exception as e:
        return f"Error: {e}"

# Create a new SQLDatabase instance for a given database name
def get_db_for_database(dbname: str):
    user = os.getenv("MYSQL_USER")
    password = os.getenv("MYSQL_PASSWORD")
    host = os.getenv("MYSQL_HOST", "localhost")
    port = os.getenv("MYSQL_PORT", "3306")
    conn_str = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{dbname}"
    engine = create_engine(conn_str)
    return SQLDatabase(engine) 