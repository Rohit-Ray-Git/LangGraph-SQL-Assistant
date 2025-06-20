# MySQL LangChain Agent

A Python agent that answers natural language questions about your MySQL database using LLMs, LangChain, and LangGraph.

## Features
- Connects to your MySQL database
- Uses LLMs to generate, validate, and execute SQL queries
- Multi-step workflow with LangGraph
- CLI interface (web UI optional)

## Setup
1. Clone this repo and enter the directory:
   ```bash
   git clone <repo-url>
   cd mysql_langchain_agent
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your MySQL and LLM credentials (see example below).

## .env Example
```
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB=your_database
OPENAI_API_KEY=sk-...
```

## Usage
Run the CLI:
```bash
python main.py
```

Then type your question (e.g. `How many orders are over $300?`).

---

## License
MIT 