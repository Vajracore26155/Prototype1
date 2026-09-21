import bcrypt

# The hash from the database
hashed_password = "$2b$12$6trlemxXIfokzg6/1Ojk3unhovdUrZtp1LOyPfqxxVDyDNiyQ1ijC"

# Test passwords
passwords_to_test = [
    "Admin@123",
    "Mayank@123",
    "admin123",
    "password123",
    "Tatva@123",
    "Mayank@123",
]

print("Testing passwords against the hash:")
for pwd in passwords_to_test:
    try:
        result = bcrypt.checkpw(pwd.encode('utf-8'), hashed_password.encode('utf-8'))
        print(f"  Password '{pwd}': {result}")
    except Exception as e:
        print(f"  Password '{pwd}': ERROR - {e}")
