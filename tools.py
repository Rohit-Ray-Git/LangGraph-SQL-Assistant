from langchain_community.utilities.sql_database import SQLDatabase

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