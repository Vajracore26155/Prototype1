import sqlite3

conn = sqlite3.connect('./data/sih26155.db')
cursor = conn.cursor()
cursor.execute('SELECT email, password_hash FROM users WHERE email = ?', ('mayankparab4811@gmail.com',))
row = cursor.fetchone()
if row:
    print(f'Email: {row[0]}')
    print(f'Password Hash: {row[1]}')
else:
    print('User not found')
conn.close()
