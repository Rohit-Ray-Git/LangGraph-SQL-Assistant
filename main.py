import sys
from db_config import get_db_engine
from langchain_community.utilities.sql_database import SQLDatabase
from agent_workflow import build_workflow, make_state

# Load DB engine and wrap with SQLDatabase
engine = get_db_engine()
db = SQLDatabase(engine)

# Build the workflow
workflow = build_workflow(db)
app = workflow.compile()

print("Welcome to the MySQL LangChain Agent! Type 'exit' to quit.")

while True:
    question = input("\nAsk a question about your database: ").strip()
    if question.lower() in ("exit", "quit"): break
    state = make_state()
    state["question"] = question
    # Run through the workflow
    result = app.invoke(state)
    print("\nAnswer:")
    print(result.get("answer", "No answer generated.")) 