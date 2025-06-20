import sys
from db_config import get_db_engine
from langchain_community.utilities.sql_database import SQLDatabase
from agent_workflow import build_workflow
import os
from datetime import datetime

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

def log_action(action: str):
    log_file = "agent_query_log.txt"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().isoformat()}] {action}\n")

while True:
    prompt_str = f"\n[{current_db}] Ask a question about your database: "
    question = input(prompt_str).strip()
    if question.lower() in ("exit", "quit"): break
    # Initialize state as a dict matching the State schema
    state = {"question": question, "query": None, "result": None, "answer": None, "current_db": current_db, "confirmation_required": False, "pending_action": None}
    # Run through the workflow
    result = app.invoke(state)
    if result is None:
        print("\n[ERROR] The workflow returned None. Please check your workflow logic or LLM/API responses.")
        log_action(f"ERROR: No result for question: {question}")
    else:
        # Update current_db if it was changed by the workflow
        if result.get("current_db"):
            current_db = result["current_db"]
        # Handle DML/DDL confirmation
        if result.get("confirmation_required"):
            print("\nAnswer:")
            print(result.get("answer", "No answer generated."))
            confirm = input("Type Y to confirm, N to cancel: ").strip().lower()
            log_action(f"Confirmation prompt for: {result.get('query')}, user response: {confirm}")
            if confirm == "y":
                # Re-invoke workflow with confirmation
                result["confirmation_required"] = False
                # Actually execute the dangerous command
                exec_result = app.invoke(result)
                print("\n[EXECUTION RESULT]:")
                print(exec_result.get("result", "No result."))
                log_action(f"Executed dangerous command: {result.get('query')}, result: {exec_result.get('result')}")
            else:
                print("\n[SKIPPED]: Dangerous command was not executed.")
                log_action(f"Skipped dangerous command: {result.get('query')}")
        else:
            print("\nAnswer:")
            print(result.get("answer", "No answer generated."))
            log_action(f"Query: {question}, Answer: {result.get('answer')}") 