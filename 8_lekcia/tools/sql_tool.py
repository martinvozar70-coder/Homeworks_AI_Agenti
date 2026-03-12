"""
Azure SQL Database Tool
=======================
Allows the agent to execute SELECT queries against an Azure SQL Server database.
Only SELECT statements are allowed for safety.

Requirements:
    pip install pyodbc python-dotenv

Environment variables (set in .env):
    AZURE_SQL_SERVER   = your-server.database.windows.net
    AZURE_SQL_DATABASE = your-database-name
    AZURE_SQL_USERNAME = your-username
    AZURE_SQL_PASSWORD = your-password
"""

import os
import pyodbc
from tools.base_tool import BaseTool


class AzureSQLTool(BaseTool):

    @property
    def name(self) -> str:
        return "sql_query"

    @property
    def description(self) -> str:
        return (
            "Execute a SELECT SQL query against the Azure SQL database. "
            "Use this to look up data, count records, find specific entries, etc. "
            "Only SELECT statements are allowed. "
            "If you are unsure of table names, use the 'sql_schema' tool first."
        )

    @property
    def input_schema(self) -> dict:
        return {
            "query": "string — a valid T-SQL SELECT statement"
        }

    def _get_connection(self) -> pyodbc.Connection:
        server = os.getenv("AZURE_SQL_SERVER")
        database = os.getenv("AZURE_SQL_DATABASE")
        username = os.getenv("AZURE_SQL_USERNAME")
        password = os.getenv("AZURE_SQL_PASSWORD")

       
        if not all([server, database, username, password]):
            raise ValueError(
                "Missing database credentials. "
                "Set AZURE_SQL_SERVER, AZURE_SQL_DATABASE, AZURE_SQL_USERNAME, AZURE_SQL_PASSWORD in .env"
            )

        conn_str = (
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={username};"
            f"PWD={password};"
            f"Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
        )
        return pyodbc.connect(conn_str)

    def run(self, inputs: dict) -> str:
        query = inputs.get("query", "").strip()

        if not query:
            return "Error: No query provided."

        # Safety check — only allow SELECT
        if not query.upper().lstrip().startswith("SELECT"):
            return "Error: Only SELECT statements are allowed."

        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(query)

            rows = cursor.fetchmany(50)  # limit to 50 rows
            columns = [col[0] for col in cursor.description]

            if not rows:
                return "Query returned no results."

            # Format as a readable table
            result_lines = [" | ".join(columns)]
            result_lines.append("-" * len(result_lines[0]))
            for row in rows:
                result_lines.append(" | ".join(str(val) for val in row))

            total_rows = len(rows)
            result = "\n".join(result_lines)
            if total_rows == 50:
                result += f"\n(Showing first 50 rows)"

            conn.close()
            return result

        except pyodbc.Error as e:
            return f"Database error: {str(e)}"


class AzureSQLSchemaTool(BaseTool):
    """
    A companion tool that lists tables and their columns.
    This helps the agent understand the database structure before writing queries.
    """

    @property
    def name(self) -> str:
        return "sql_schema"

    @property
    def description(self) -> str:
        return (
            "List all tables in the database and their column names. "
            "Use this FIRST before writing SQL queries, to understand what data is available."
        )

    @property
    def input_schema(self) -> dict:
        return {
            "table_name": "string (optional) — if provided, shows columns for that specific table only"
        }

    def _get_connection(self) -> pyodbc.Connection:
        # Same connection logic as AzureSQLTool
        server = os.getenv("AZURE_SQL_SERVER")
        database = os.getenv("AZURE_SQL_DATABASE")
        username = os.getenv("AZURE_SQL_USERNAME")
        password = os.getenv("AZURE_SQL_PASSWORD")

        conn_str = (
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={username};"
            f"PWD={password};"
            f"Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
        )
        breakpoint()  # Debug: Check connection string before connecting
        return pyodbc.connect(conn_str)

    def run(self, inputs: dict) -> str:
        table_name = inputs.get("table_name", "").strip()

        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            if table_name:
                # Show columns for a specific table
                cursor.execute("""
                    SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_NAME = ?
                    ORDER BY ORDINAL_POSITION
                """, table_name)
                rows = cursor.fetchall()
                if not rows:
                    return f"Table '{table_name}' not found."
                lines = [f"Columns in '{table_name}':"]
                for row in rows:
                    lines.append(f"  - {row[0]} ({row[1]}, nullable: {row[2]})")
                conn.close()
                return "\n".join(lines)
            else:
                # List all tables
                cursor.execute("""
                    SELECT TABLE_NAME
                    FROM INFORMATION_SCHEMA.TABLES
                    WHERE TABLE_TYPE = 'BASE TABLE'
                    ORDER BY TABLE_NAME
                """)
                rows = cursor.fetchall()
                if not rows:
                    return "No tables found in database."
                table_names = [row[0] for row in rows]
                conn.close()
                return "Tables in database:\n" + "\n".join(f"  - {t}" for t in table_names)

        except pyodbc.Error as e:
            return f"Database error: {str(e)}"
