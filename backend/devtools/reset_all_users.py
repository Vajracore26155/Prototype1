import sqlite3
import hashlib
import secrets

db_path = './data/sih26155.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create admin user with SHA256 hashing
admin_password = "Admin123"
salt = secrets.token_hex(16)
iterations = 100000
dk = hashlib.pbkdf2_hmac('sha256', admin_password.encode('utf-8'), salt.encode('utf-8'), iterations)
hashed = f"{salt}${dk.hex()}"

cursor.execute('''
    INSERT INTO users (user_id, email, username, hashed_password, full_name, organization_id, role, is_active, is_verified, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
''', ('USR-000001', 'mayankparab4811@gmail.com', 'admin', hashed, 'Admin User', 1, 'SUPER_ADMIN', 1, 1))

conn.commit()
print("✓ Admin user created: mayankparab4811@gmail.com / Admin123")
conn.close()
