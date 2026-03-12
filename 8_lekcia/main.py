"""
main.py — Entry point for the ReAct Agent demo
===============================================

Usage:
    python main.py

Environment variables needed (copy .env.example to .env and fill in):
    OPENAI_API_KEY
    AZURE_SQL_SERVER
    AZURE_SQL_DATABASE
    AZURE_SQL_USERNAME
    AZURE_SQL_PASSWORD
"""

import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

from agent.react_agent import ReActAgent
from tools.sql_tool import AzureSQLTool, AzureSQLSchemaTool
from tools.wikipedia_tool import WikipediaTool

breakpoint()  # Debug: Check if environment variables are loaded correctly
print("Environment variables loaded:")
print("OPENAI_API_KEY:", "Loaded" if "OPENAI_API_KEY" in os.environ else "Not found")
print("AZURE_SQL_SERVER:", os.getenv("AZURE_SQL_SERVER"))
print("AZURE_SQL_DATABASE:", os.getenv("AZURE_SQL_DATABASE"))
print("AZURE_SQL_USERNAME:", os.getenv("AZURE_SQL_USERNAME"))
print("AZURE_SQL_PASSWORD:", "Loaded" if "AZURE_SQL_PASSWORD" in os.environ else "Not found")

def main():
    # --- Initialize tools ---
    tools = [
        AzureSQLSchemaTool(),   # lets agent discover DB structure
        AzureSQLTool(),         # lets agent query the DB
        WikipediaTool(),        # lets agent look up general knowledge
    ]

    # --- Initialize the ReAct agent ---
    agent = ReActAgent(
        tools=tools,
        model="gpt-4o-mini",   # cheaper model, good for demos; swap to gpt-4o for better results
        max_steps=10,
    )

    # --- Example questions ---
    # Mix of questions that require DB queries and general knowledge
    questions = [
        # Database question — agent will discover schema, then query
        "What tables exist in the database? Show me a sample of data from one of them.",

        # Wikipedia question
        "What is the ReAct pattern in AI agents?",

        # Combined question (agent decides which tools to use)
        "How many records are in the database, and what is Azure SQL Server according to Wikipedia?",
    ]

    print("\n" + "="*60)
    print("  ReAct Agent — AI_AGENTI Homework")
    print("="*60)

    # Run a single question interactively, or loop through examples
    print("\nRunning example questions...\n")
    print("(Set verbose=True to see the full Thought/Action/Observation loop)\n")

    # Run just the first question as a demo
    answer = agent.run(questions[0], verbose=True)

    # Comment/Uncomment to run all questions:
    for q in questions:
         agent.run(q, verbose=True)
         print()


if __name__ == "__main__":
    main()
