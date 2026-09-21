import sqlite3
from datetime import datetime

db_path = './data/sih26155.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# First create organization
cursor.execute('''
    INSERT INTO organizations (org_id, name, slug, status, created_at, updated_at)
    VALUES (?, ?, ?, ?, datetime('now'), datetime('now'))
''', ('ORG-000001', 'Admin Organization', 'admin-org', 'ACTIVE'))

conn.commit()

# Get the org ID
org_id = cursor.lastrowid

# Create admin user with plain password (for development)
admin_password = "Admin123"

cursor.execute('''
    INSERT INTO users (user_id, email, username, hashed_password, full_name, organization_id, role, is_active, is_verified, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
''', ('USR-000001', 'mayankparab4811@gmail.com', 'admin', admin_password, 'Admin User', org_id, 'SUPER_ADMIN', 1, 1))

conn.commit()
print(f"✓ Organization created with ID: {org_id}")
print("✓ Admin user created: mayankparab4811@gmail.com / Admin123")
conn.close()
