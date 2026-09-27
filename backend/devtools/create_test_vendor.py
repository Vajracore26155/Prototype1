import sqlite3
from datetime import datetime
import uuid

conn = sqlite3.connect('./data/sih26155.db')
cursor = conn.cursor()

# Create test vendor data based on existing APPROVED vendor template
test_email = 'testapproved@company.com'
test_name = 'Test Vendor Company'
vendor_id = f'VND-{uuid.uuid4().hex[:6].upper()}'
now = datetime.utcnow().isoformat()

# Insert new approved vendor
cursor.execute('''
    INSERT INTO vendor_users 
    (vendor_id, email, company_name, contact_name, phone, email_verified, 
     is_active, approval_status, approved_by, approved_at, organization_id, 
     created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', (vendor_id, test_email, test_name, 'Test Contact', '+1234567890', 
      0, 1, 'APPROVED', 'admin@platform.com', now, 1, now, now))

conn.commit()
db_id = cursor.lastrowid

# Verify insertion
cursor.execute('SELECT id, vendor_id, email, company_name, approval_status FROM vendor_users WHERE id = ?', (db_id,))
result = cursor.fetchone()
print(f'✓ Created approved test vendor:')
print(f'  Database ID: {result[0]}')
print(f'  Vendor ID: {result[1]}')
print(f'  Email: {result[2]}')
print(f'  Company: {result[3]}')
print(f'  Status: {result[4]}')
print()
print('Ready to test OTP flow with this vendor.')

conn.close()
