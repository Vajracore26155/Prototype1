import sqlite3

db_path = './data/sih26155.db'
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"Tables found: {len(tables)}")
    for table in tables:
        print(f"  - {table[0]}")
    
    # Check vendor_users table
    print("\nvendor_users table columns:")
    cursor.execute("PRAGMA table_info(vendor_users)")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    conn.close()
except FileNotFoundError:
    print(f"Database file not found: {db_path}")
except Exception as e:
    print(f"Error: {e}")
