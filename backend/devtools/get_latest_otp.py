import sqlite3
from datetime import datetime

db_path = "./data/sih26155.db"

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get vendor
vendor_email = "vendor97269@test.com"
cursor.execute("SELECT id, vendor_id FROM vendor_users WHERE email = ?", (vendor_email,))
vendor = cursor.fetchone()

if not vendor:
    print(f"✗ Vendor not found: {vendor_email}")
    exit(1)

vendor_id = vendor["id"]
print(f"Vendor ID (DB): {vendor_id}")
print(f"Vendor Email: {vendor_email}")
print()

# Get most recent OTP
cursor.execute("""
    SELECT otp_id, otp_code, otp_hash, expires_at, is_used, created_at
    FROM vendor_otps
    WHERE vendor_id = ?
    ORDER BY created_at DESC
    LIMIT 1
""", (vendor_id,))

otp = cursor.fetchone()

if not otp:
    print("✗ No OTP found")
    exit(1)

print("Latest OTP:")
print(f"  OTP ID: {otp['otp_id']}")
print(f"  OTP Code: {otp['otp_code']}")
print(f"  Is Used: {otp['is_used']}")
print(f"  Created: {otp['created_at']}")
print(f"  Expires: {otp['expires_at']}")

conn.close()
