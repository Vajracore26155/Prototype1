#!/usr/bin/env python3
"""
Check all vendors in the system and their details
"""
import sqlite3
from datetime import datetime

db_path = "./data/sih26155.db"

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("=" * 100)
print("VENDOR INVENTORY REPORT")
print("=" * 100)
print()

# Get total count
cursor.execute("SELECT COUNT(*) as count FROM vendor_users")
total_vendors = cursor.fetchone()["count"]

print(f"TOTAL VENDORS IN SYSTEM: {total_vendors}")
print()

# Get vendors by status
cursor.execute("""
    SELECT 
        approval_status,
        COUNT(*) as count
    FROM vendor_users
    GROUP BY approval_status
    ORDER BY count DESC
""")

statuses = cursor.fetchall()
print("VENDORS BY STATUS:")
print("-" * 50)
for row in statuses:
    print(f"  {row['approval_status']:15} : {row['count']:3} vendors")
print()

# List all vendors
print("=" * 100)
print("DETAILED VENDOR LIST")
print("=" * 100)
print()

cursor.execute("""
    SELECT 
        id,
        vendor_id,
        email,
        contact_name,
        company_name,
        approval_status,
        password_hash,
        created_at
    FROM vendor_users
    ORDER BY created_at DESC
""")

vendors = cursor.fetchall()

print(f"{'ID':3} | {'Vendor ID':10} | {'Email':35} | {'Contact Name':20} | {'Company':20} | {'Status':10} | {'Has Password':12} | {'Created'}")
print("-" * 160)

for vendor in vendors:
    has_password = "YES" if vendor["password_hash"] else "NO"
    created = vendor["created_at"][:10] if vendor["created_at"] else "N/A"
    
    print(f"{vendor['id']:3} | {vendor['vendor_id']:10} | {vendor['email']:35} | {vendor['contact_name']:20} | {vendor['company_name']:20} | {vendor['approval_status']:10} | {has_password:12} | {created}")

print()
print("=" * 100)

# Check uploads
cursor.execute("SELECT COUNT(*) as count FROM vendor_uploads")
total_uploads = cursor.fetchone()["count"]
print(f"Total Uploads: {total_uploads}")

# Check upload sessions
cursor.execute("SELECT COUNT(*) as count FROM vendor_upload_sessions WHERE status = 'ACTIVE'")
active_sessions = cursor.fetchone()["count"]
print(f"Active Upload Sessions: {active_sessions}")

# Check OTPs
cursor.execute("SELECT COUNT(*) as count FROM vendor_otps")
total_otps = cursor.fetchone()["count"]
print(f"Total OTP Records: {total_otps}")

print()
print("DATABASE LOCATION: ./data/sih26155.db")
print("=" * 100)

conn.close()
