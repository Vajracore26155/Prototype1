import sqlite3
from datetime import datetime

conn = sqlite3.connect('./data/sih26155.db')
cursor = conn.cursor()

# Create approved vendor for the test email
cursor.execute('''
    INSERT INTO vendor_users 
    (vendor_id, email, company_name, contact_name, phone, email_verified, 
     is_active, approval_status, approved_by, approved_at, organization_id, 
     created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', ('VND-KINGPML', 'kingpml42@gmail.com', 'KingPML Company', 'King PML', '+91-9999999999',
      0, 1, 'APPROVED', 'admin@platform.com', datetime.utcnow().isoformat(), 1, 
      datetime.utcnow().isoformat(), datetime.utcnow().isoformat()))

conn.commit()

# Verify
cursor.execute("SELECT id, vendor_id, email, approval_status FROM vendor_users WHERE email = 'kingpml42@gmail.com'")
result = cursor.fetchone()

if result:
    print(f'✓ Created vendor for kingpml42@gmail.com')
    print(f'  Database ID: {result[0]}')
    print(f'  Vendor ID: {result[1]}')
    print(f'  Email: {result[2]}')
    print(f'  Status: {result[3]}')
    print()
    print('Now you can test OTP login with kingpml42@gmail.com in the frontend!')
else:
    print('Error creating vendor')

conn.close()
