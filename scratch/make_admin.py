import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), '..', 'instance', 'database.db')
conn = sqlite3.connect(db_path)
conn.execute("UPDATE users SET role='admin' WHERE username='testuser'")
conn.commit()
conn.close()
print("Updated testuser to admin role.")
