import sqlite3
import os
from werkzeug.security import generate_password_hash

db_path = 'e:/dark moniter/darkweb_monitor/instance/darkweb_monitor.db'
new_password = "Admin@123"
email = "admin@gmail.com"

if not os.path.exists(db_path):
    print("Database not found.")
    exit(1)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    new_hash = generate_password_hash(new_password)
    
    cursor.execute("UPDATE user SET password=? WHERE email=?", (new_hash, email))
    conn.commit()
    
    if cursor.rowcount > 0:
        print(f"Successfully updated password for {email} to: {new_password}")
    else:
        print(f"User {email} not found in database.")
        
    conn.close()
except Exception as e:
    print(f"Error: {e}")
