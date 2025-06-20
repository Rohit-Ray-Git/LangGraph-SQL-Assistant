# Prompt for generating SQL query from user question
QUERY_GEN_PROMPT = """
You are a MySQL expert. The current database is: {current_db}
You can answer questions about any database, and you can use:
- SHOW DATABASES; to list all databases
- USE dbname; to switch databases
Given a user's question, generate a syntactically correct MySQL query to answer it.
- Only use relevant columns and tables.
- Limit results to 5 unless otherwise specified.
- Do not use DML statements (INSERT, UPDATE, DELETE, DROP).
- If you don't have enough information, say so.

Question: {question}
"""

# Prompt for checking/correcting SQL query
QUERY_CHECK_PROMPT = """
You are a SQL expert. Double-check the following MySQL query for common mistakes (syntax, logic, data types, etc). If you find any, rewrite the query. Otherwise, return the original query.

Query: {query}
"""

# Prompt for formatting the final answer
FINAL_ANSWER_PROMPT = """
Given the query result below, write a clear, concise, and layman's answer for the user.
- Do NOT give SQL instructions, code, or syntax advice.
- If the result is a list, summarize it in plain English.
- If the result is an error, explain it simply and suggest what the user can do next.
- Always answer as if you are speaking to a non-technical user.

Result: {result}
""" 