import streamlit as st
from agent_workflow import build_workflow
from db_config import get_db_engine
from langchain_community.utilities.sql_database import SQLDatabase
import os
from datetime import datetime

# --- Helper for logging ---
LOG_FILE = "agent_query_log.txt"
def log_action(action: str):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().isoformat()}] {action}\n")

def read_log():
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        return f.readlines()

# --- Streamlit UI ---
st.set_page_config(page_title="MySQL LangChain Agent", page_icon="🗄️", layout="wide")
st.title("🗄️ MySQL LangChain Agent")
st.markdown("""
A professional, user-friendly SQL agent powered by LLMs, LangChain, and LangGraph.\
Ask natural language questions about your MySQL database, switch databases, and safely run queries.\
**Dangerous commands require confirmation.**
""")

# --- Session State ---
def get_default_db():
    return os.getenv("MYSQL_DB")

def get_workflow_and_db(current_db):
    engine = get_db_engine()
    db = SQLDatabase(engine)
    workflow = build_workflow(db)
    return workflow.compile(), db

if "current_db" not in st.session_state:
    st.session_state.current_db = get_default_db()
if "pending_result" not in st.session_state:
    st.session_state.pending_result = None
if "pending_state" not in st.session_state:
    st.session_state.pending_state = None

# --- Sidebar: Query Log ---
st.sidebar.header("Query Log 📝")
log_lines = read_log()
if log_lines:
    st.sidebar.text_area("Log", value="".join(log_lines[-30:]), height=400)
else:
    st.sidebar.info("No queries logged yet.")

# --- Main UI ---
st.markdown(f"**Current Database:** `{st.session_state.current_db}`")

with st.form("query_form", clear_on_submit=True):
    question = st.text_input("Ask a question about your database:", key="question_input")
    submitted = st.form_submit_button("Submit", use_container_width=True)

if submitted and question:
    # Prepare state
    state = {
        "question": question,
        "query": None,
        "result": None,
        "answer": None,
        "current_db": st.session_state.current_db,
        "confirmation_required": False,
        "pending_action": None
    }
    workflow, db = get_workflow_and_db(st.session_state.current_db)
    result = workflow.invoke(state)
    log_action(f"Query: {question}")
    # Handle dangerous command confirmation
    if result.get("confirmation_required"):
        st.session_state.pending_result = result
        st.session_state.pending_state = state
        st.warning(result.get("answer", "Confirmation required."))
    else:
        # Update current_db if changed
        if result.get("current_db"):
            st.session_state.current_db = result["current_db"]
        st.success(result.get("answer", "No answer generated."))
        log_action(f"Answer: {result.get('answer')}")

# --- Dangerous Command Confirmation ---
if st.session_state.pending_result:
    with st.expander("⚠️ Dangerous Command Confirmation", expanded=True):
        st.write(st.session_state.pending_result.get("result"))
        col1, col2 = st.columns(2)
        confirm = col1.button("Yes, execute", type="primary")
        cancel = col2.button("No, cancel", type="secondary")
        if confirm:
            # Re-invoke workflow with confirmation
            st.session_state.pending_result["confirmation_required"] = False
            workflow, db = get_workflow_and_db(st.session_state.current_db)
            exec_result = workflow.invoke(st.session_state.pending_result)
            st.success(f"[EXECUTION RESULT]: {exec_result.get('result', 'No result.')}" )
            log_action(f"Executed dangerous command: {st.session_state.pending_result.get('query')}, result: {exec_result.get('result')}")
            st.session_state.pending_result = None
            st.session_state.pending_state = None
        elif cancel:
            st.info("[SKIPPED]: Dangerous command was not executed.")
            log_action(f"Skipped dangerous command: {st.session_state.pending_result.get('query')}")
            st.session_state.pending_result = None
            st.session_state.pending_state = None

st.markdown("---")
st.caption("Made with ❤️ using LangChain, LangGraph, and Streamlit. | [GitHub](https://github.com/Rohit-Ray-Git/LangGraph-SQL-Assistant)") 