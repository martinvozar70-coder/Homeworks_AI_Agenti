"""
test_sql_connection.py
======================
Run this script to troubleshoot your Azure SQL connection step by step.

Usage:
    python test_sql_connection.py
"""

import os
from dotenv import load_dotenv

load_dotenv()

# --- Step 1: Check environment variables ---
print("=== STEP 1: Checking .env variables ===")
server   = os.getenv("AZURE_SQL_SERVER")
database = os.getenv("AZURE_SQL_DATABASE")
username = os.getenv("AZURE_SQL_USERNAME")
password = os.getenv("AZURE_SQL_PASSWORD")

print(f"  AZURE_SQL_SERVER:   {server   or '❌ NOT SET'}")
print(f"  AZURE_SQL_DATABASE: {database or '❌ NOT SET'}")
print(f"  AZURE_SQL_USERNAME: {username or '❌ NOT SET'}")
print(f"  AZURE_SQL_PASSWORD: {'✅ set (hidden)' if password else '❌ NOT SET'}")

if not all([server, database, username, password]):
    print("\n❌ Fix the missing variables in your .env file first, then re-run.")
    exit(1)

print("  ✅ All variables loaded\n")


# --- Step 2: Check pyodbc is installed ---
print("=== STEP 2: Checking pyodbc ===")
try:
    import pyodbc
    print(f"  ✅ pyodbc version: {pyodbc.version}\n")
except ImportError:
    print("  ❌ pyodbc not installed. Run: uv pip install pyodbc")
    exit(1)


# --- Step 3: Check available ODBC drivers ---
print("=== STEP 3: Available ODBC drivers on your machine ===")
drivers = pyodbc.drivers()
if not drivers:
    print("  ❌ No ODBC drivers found!")
    print("  → Download ODBC Driver 18 from:")
    print("    https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server")
else:
    for d in drivers:
        marker = "✅" if "SQL Server" in d else "  "
        print(f"  {marker} {d}")

sql_drivers = [d for d in drivers if "SQL Server" in d]
if not sql_drivers:
    print("\n  ❌ No SQL Server ODBC driver found — install it from the link above.")
    exit(1)

# Pick the best available driver
preferred = ["ODBC Driver 18 for SQL Server", "ODBC Driver 17 for SQL Server"]
driver = next((d for d in preferred if d in sql_drivers), sql_drivers[0])
print(f"\n  → Using driver: {driver}\n")


# --- Step 4: Try to connect ---
print("=== STEP 4: Attempting connection ===")
conn_str = (
    f"DRIVER={{{driver}}};"
    f"SERVER={server};"
    f"DATABASE={database};"
    f"UID={username};"
    f"PWD={password};"
    f"Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
)

try:
    conn = pyodbc.connect(conn_str, timeout=10)
    print("  ✅ Connection successful!\n")
except pyodbc.Error as e:
    print(f"  ❌ Connection failed: {e}\n")
    print("  Common causes:")
    print("  - Wrong server name (should be: yourserver.database.windows.net)")
    print("  - Wrong username or password")
    print("  - Your IP is not whitelisted in Azure firewall")
    print("    → Go to Azure Portal → SQL Server → Networking → Add your IP")
    print("  - Database name is wrong")
    exit(1)


# --- Step 5: List tables ---
print("=== STEP 5: Listing tables in the database ===")
try:
    cursor = conn.cursor()
    cursor.execute("""
        SELECT TABLE_NAME 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_NAME
    """)
    tables = cursor.fetchall()
    if tables:
        print(f"  ✅ Found {len(tables)} table(s):")
        for t in tables:
            print(f"     - {t[0]}")
    else:
        print("  ⚠️  Connected, but no tables found in this database.")
    conn.close()
except pyodbc.Error as e:
    print(f"  ❌ Query failed: {e}")
    exit(1)

print("\n✅ All checks passed — your SQL connection is working!")
print("   You can now run: python main.py")