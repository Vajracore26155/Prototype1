import sqlite3

db_path = './data/sih26155.db'
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Add missing password_hash column to vendor_users
    print("Adding password_hash column to vendor_users...")
    cursor.execute("""
        ALTER TABLE vendor_users 
        ADD COLUMN password_hash VARCHAR(255) NULL
    """)
    conn.commit()
    print("✓ Column added successfully")
    
    # Verify
    cursor.execute("PRAGMA table_info(vendor_users)")
    columns = cursor.fetchall()
    print("\nUpdated vendor_users columns:")
    for col in columns:
        if col[1] == 'password_hash':
            print(f"  ✓ {col[1]} ({col[2]})")
        else:
            print(f"    {col[1]} ({col[2]})")
    
    conn.close()
    print("\nSchema fixed!")
except sqlite3.OperationalError as e:
    if "duplicate column" in str(e):
        print("✓ Column already exists")
    else:
        print(f"Error: {e}")
except Exception as e:
    print(f"Error: {e}")
