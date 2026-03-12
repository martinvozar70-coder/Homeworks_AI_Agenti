# AI Agent — Homework (AI_AGENTI / robot_dreams_cz)

A **ReAct agent** implemented in pure Python (no heavy framework) that answers questions using two tools:
- **Azure SQL Database** — queries structured data
- **Wikipedia** — looks up general knowledge

---

## What is a ReAct Agent?

ReAct (Reasoning + Acting) is an agent pattern where the LLM alternates between:

```
Thought: What do I need to find out?
Action: <tool_name>
Action Input: {"parameter": "value"}
Observation: <tool result>
... (repeat) ...
Final Answer: <answer to the user>
```

This makes the agent's reasoning **transparent and debuggable** — you can see every step.

---

## Project Structure

```
ai_agent_homework/
├── agent/
│   └── react_agent.py      # ReAct loop implementation
├── tools/
│   ├── base_tool.py        # Abstract base class for all tools
│   ├── sql_tool.py         # Azure SQL (schema discovery + SELECT queries)
│   └── wikipedia_tool.py   # Wikipedia search
├── main.py                 # Entry point / demo
├── requirements.txt
├── .env.example            # Template for credentials
└── README.md
```

---

## Setup

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/ai-agent-homework.git
cd ai-agent-homework
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

> **Note for Windows users:** You need the [ODBC Driver 18 for SQL Server](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server) installed.

### 4. Configure credentials
```bash
cp .env.example .env
# Edit .env with your actual credentials
```

Your `.env` should look like:
```
OPENAI_API_KEY=sk-...
AZURE_SQL_SERVER=myserver.database.windows.net
AZURE_SQL_DATABASE=mydatabase
AZURE_SQL_USERNAME=myuser
AZURE_SQL_PASSWORD=mypassword
```

### 5. Run the agent
```bash
python main.py
```

---

## Example Output

```
============================================================
QUESTION: What tables exist in the database? Show me a sample.
============================================================

--- Step 1 ---
Thought: I should first discover what tables exist in the database.
Action: sql_schema
Action Input: {}

Observation: Tables in database:
  - customers
  - orders
  - products

--- Step 2 ---
Thought: Let me look at the customers table structure and then get some sample data.
Action: sql_schema
Action Input: {"table_name": "customers"}

Observation: Columns in 'customers':
  - id (int, nullable: NO)
  - name (nvarchar, nullable: NO)
  - email (nvarchar, nullable: YES)

--- Step 3 ---
Thought: Now I'll get a sample of data from the customers table.
Action: sql_query
Action Input: {"query": "SELECT TOP 5 * FROM customers"}

Observation: id | name | email
...

Final Answer: The database contains 3 tables: customers, orders, products.
Here is sample data from the customers table: ...
```

---

## Design Decisions

| Choice | Rationale |
|--------|-----------|
| **Custom framework** | Easier to understand than LangChain — every line is visible |
| **ReAct pattern** | Simple loop, debuggable, well-documented in literature |
| **SQL + Wikipedia** | Different tool types: structured data vs free-text knowledge |
| **Only SELECT allowed** | Safety — agent cannot modify the database |
| **Schema tool** | Agent discovers DB structure dynamically, no hardcoding |

---

## Extending the Agent

To add a new tool:

1. Create a file in `tools/`, inherit from `BaseTool`
2. Implement `name`, `description`, `input_schema`, and `run()`
3. Add it to the `tools` list in `main.py`

```python
class MyTool(BaseTool):
    @property
    def name(self): return "my_tool"

    @property
    def description(self): return "Does something useful."

    @property
    def input_schema(self): return {"input": "string"}

    def run(self, inputs): return f"Result for: {inputs['input']}"
```

---

## References

- Yao et al. (2022) — *ReAct: Synergizing Reasoning and Acting in Language Models* — https://arxiv.org/abs/2210.03629
- OpenAI API docs — https://platform.openai.com/docs
- Azure SQL connectivity — https://learn.microsoft.com/en-us/azure/azure-sql/
