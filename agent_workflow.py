# LangGraph workflow for MySQL LangChain Agent
from langgraph.graph import StateGraph, START, END
from langchain_community.utilities.sql_database import SQLDatabase
import openai
from prompts import QUERY_GEN_PROMPT, QUERY_CHECK_PROMPT, FINAL_ANSWER_PROMPT
from db_config import get_openai_api_key
from typing import TypedDict, Optional
from tools import safe_query, list_databases, get_db_for_database
import re

class State(TypedDict):
    question: Optional[str]
    query: Optional[str]
    result: Optional[str]
    answer: Optional[str]
    current_db: Optional[str]  # Track the current database
    confirmation_required: Optional[bool]  # For DML/DDL confirmation
    pending_action: Optional[str]  # For DML/DDL confirmation

# Helper to call OpenAI LLM
openai.api_key = get_openai_api_key()

DANGEROUS_SQL = re.compile(r"\\b(drop|delete|truncate|alter|update)\\b", re.IGNORECASE)

def call_llm(prompt, **kwargs):
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": prompt}],
            **kwargs
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"LLM Error: {e}"

# Node: Generate SQL query from question (LLM call)
def generate_query_node(state: State) -> State:
    prompt = QUERY_GEN_PROMPT.format(question=state["question"], current_db=state.get("current_db"))
    sql = call_llm(prompt)
    state["query"] = sql
    return state

# Node: Check/correct SQL query (LLM call)
def check_query_node(state: State) -> State:
    # Detect dangerous commands
    if state["query"] and DANGEROUS_SQL.search(state["query"]):
        state["confirmation_required"] = True
        state["pending_action"] = "dml_ddl"
        state["result"] = f"[CONFIRMATION REQUIRED] The following command is potentially dangerous: {state['query']}\nDo you want to execute it? (Y/N)"
        state["answer"] = state["result"]
        return state
    # Detect SHOW DATABASES
    if state["query"] and re.match(r"^\s*show\s+databases", state["query"], re.IGNORECASE):
        db = get_db_for_database(state["current_db"] or "information_schema")
        dbs = list_databases(db)
        state["result"] = dbs
        # Do not set state["answer"] here; let format_answer_node handle it
        return state
    # Detect USE dbname
    m = re.match(r"^\s*use\s+([a-zA-Z0-9_]+)", state["query"] or "", re.IGNORECASE)
    if m:
        new_db = m.group(1)
        try:
            db = get_db_for_database(new_db)
            _ = db.get_usable_table_names()
            state["current_db"] = new_db
            state["result"] = f"Switched to database: {new_db}"
            # Do not set state["answer"] here; let format_answer_node handle it
        except Exception as e:
            state["result"] = f"Error switching database: {e}"
            # Do not set state["answer"] here; let format_answer_node handle it
        return state
    # Otherwise, normal check
    prompt = QUERY_CHECK_PROMPT.format(query=state["query"])
    checked_sql = call_llm(prompt)
    state["query"] = checked_sql
    return state

# Node: Execute SQL query
def execute_query_node(state: State, db: SQLDatabase) -> State:
    # If the state has switched current_db, use the new db connection
    db_to_use = db
    if state.get("current_db"):
        db_to_use = get_db_for_database(state["current_db"])
    state["result"] = safe_query(db_to_use, state["query"])
    return state

# Node: Format final answer (LLM call)
def format_answer_node(state: State) -> State:
    prompt = FINAL_ANSWER_PROMPT.format(result=state["result"])
    answer = call_llm(prompt)
    state["answer"] = answer
    return state

# Build the workflow
def build_workflow(db: SQLDatabase):
    workflow = StateGraph(State)
    workflow.add_node("generate_query", generate_query_node)
    workflow.add_node("check_query", check_query_node)
    workflow.add_node("execute_query", lambda state: execute_query_node(state, db))
    workflow.add_node("format_answer", format_answer_node)
    workflow.add_edge(START, "generate_query")
    workflow.add_edge("generate_query", "check_query")
    workflow.add_edge("check_query", "execute_query")
    workflow.add_edge("execute_query", "format_answer")
    workflow.add_edge("format_answer", END)
    return workflow 