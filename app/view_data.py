import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect("aadhaar_data.db")
cursor = conn.cursor()

# Fetch all records from the aadhaar table
cursor.execute("SELECT * FROM aadhaar")
rows = cursor.fetchall()

# Print the records
print("\nStored Aadhaar Records:")
print("-" * 50)
for row in rows:
    print(f"ID: {row[0]}")
    print(f"Aadhaar Number: {row[1]}")
    print(f"Fingerprint ID: {row[2]}")
    print(f"Location: {row[3]}")
    print("-" * 50)

# Close the database connection
conn.close()