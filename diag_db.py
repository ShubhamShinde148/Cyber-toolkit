import sqlite3
import os
from werkzeug.security import check_password_hash

db_path = 'e:/dark moniter/darkweb_monitor/instance/darkweb_monitor.db'

print(f"Checking database at: {db_path}")
if os.path.exists(db_path):
    print("Database file exists.")
else:
    print("ERROR: Database file NOT found.")
    exit(1)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if 'user' table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user'")
    if cursor.fetchone():
        print("Table 'user' exists.")
    else:
        print("ERROR: Table 'user' NOT found.")
        exit(1)
        
    # Get user info
    cursor.execute("SELECT username, email, password FROM user WHERE email='admin@gmail.com'")
    row = cursor.fetchone()
    if row:
        username, email, stored_hash = row
        print(f"User found: {username} ({email})")
        print(f"Stored Hash: {stored_hash}")
        
        # Test a common password if you want, or just verify format
        if stored_hash.startswith('scrypt:'):
            print("Hash format: scrypt (Werkzeug 3.x+)")
        elif stored_hash.startswith('pbkdf2:sha256:'):
            print("Hash format: pbkdf2:sha256 (Werkzeug 2.x)")
        else:
            print("Hash format: Unknown/Other")
            
    else:
        print("User 'admin@gmail.com' NOT found in SQLite.")
        
    conn.close()
except Exception as e:
    print(f"Database error: {e}")
