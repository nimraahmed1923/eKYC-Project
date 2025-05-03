import sqlite3

# Connect to your database
conn = sqlite3.connect("ekyc.db")  # Use your actual path if different
cursor = conn.cursor()

# Add the fingerprint column (run this only once)
try:
    cursor.execute("ALTER TABLE ekyc_data ADD COLUMN fingerprint TEXT")
    print("✅ 'fingerprint' column added to ekyc_data.")
except sqlite3.OperationalError as e:
    print(f"⚠️ Skipping: {e}")

conn.commit()
conn.close()
