import sys
from db_config import get_db_engine
from langchain_community.utilities.sql_database import SQLDatabase
from agent_workflow import build_workflow
import os

# Load DB engine and wrap with SQLDatabase
engine = get_db_engine()
db = SQLDatabase(engine)

# Get the default database from the environment
DEFAULT_DB = os.getenv("MYSQL_DB")

# Build the workflow
workflow = build_workflow(db)
app = workflow.compile()

print("Welcome to the MySQL LangChain Agent! Type 'exit' to quit.")

current_db = DEFAULT_DB

while True:
    prompt_str = f"\n[{current_db}] Ask a question about your database: "
    question = input(prompt_str).strip()
    if question.lower() in ("exit", "quit"): break
    # Initialize state as a dict matching the State schema
    state = {"question": question, "query": None, "result": None, "answer": None, "current_db": current_db}
    # Run through the workflow
    result = app.invoke(state)
    if result is None:
        print("\n[ERROR] The workflow returned None. Please check your workflow logic or LLM/API responses.")
    else:
        # Update current_db if it was changed by the workflow
        if result.get("current_db"):
            current_db = result["current_db"]
        print("\nAnswer:")
        print(result.get("answer", "No answer generated.")) 