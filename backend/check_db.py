import sqlite3

conn = sqlite3.connect('/app/data/frontend_efimero.db')
cursor = conn.cursor()

# List all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables in database:", tables)

# If usuarios exists, show its structure
if ('usuarios',) in tables:
    cursor.execute("PRAGMA table_info(usuarios)")
    columns = cursor.fetchall()
    print("\nUsuarios table structure:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
else:
    print("\n❌ Table 'usuarios' does NOT exist!")

conn.close()
