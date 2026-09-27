import sqlite3
import bcrypt

db_path = './data/sih26155.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# New password (must be within 72 bytes)
new_password = "Admin123"  # Simple, under 72 bytes
password_bytes = new_password.encode('utf-8')[:72]
salt = bcrypt.gensalt(rounds=12)
hashed = bcrypt.hashpw(password_bytes, salt).decode('utf-8')

print(f"New password hash: {hashed}")

# Update admin user password
cursor.execute(
    'UPDATE users SET hashed_password = ? WHERE email = ?',
    (hashed, 'mayankparab4811@gmail.com')
)
conn.commit()

print("✓ Admin password reset to: Admin123")
conn.close()
