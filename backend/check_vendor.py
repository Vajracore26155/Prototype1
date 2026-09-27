import sqlite3

conn = sqlite3.connect('./data/sih26155.db')
cursor = conn.cursor()

# Check if kingpml42@gmail.com exists
cursor.execute("SELECT id, email, approval_status FROM vendor_users WHERE email = 'kingpml42@gmail.com'")
result = cursor.fetchone()

if result:
    print(f'Found: ID={result[0]}, Email={result[1]}, Status={result[2]}')
else:
    print('❌ kingpml42@gmail.com NOT FOUND in database')
    print('This vendor needs to be registered and approved first.')

# Show the test vendor we created
print()
cursor.execute("SELECT id, email, approval_status FROM vendor_users WHERE email = 'testapproved@company.com'")
result = cursor.fetchone()
if result:
    print(f'✓ Test vendor available: ID={result[0]}, Email={result[1]}, Status={result[2]}')

conn.close()
