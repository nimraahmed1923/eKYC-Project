import sqlite3
import csv

DB_PATH = "aadhaar_data.db"

# Export to CSV
def export_to_csv(csv_file="aadhaar_data.csv"):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM aadhaar")
    data = cursor.fetchall()
    headers = [description[0] for description in cursor.description]

    with open(csv_file, "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(data)

    conn.close()
    print(f"Data exported to {csv_file}")

# Search
def search_data(keyword):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    query = "SELECT * FROM aadhaar WHERE aadhaar_number LIKE ? OR location LIKE ?"
    cursor.execute(query, (f"%{keyword}%", f"%{keyword}%"))
    results = cursor.fetchall()
    conn.close()

    if results:
        for row in results:
            print(row)
    else:
        print("No data found for the keyword.")

# Delete
def delete_data(aadhaar_number):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM aadhaar WHERE aadhaar_number = ?", (aadhaar_number,))
    conn.commit()
    conn.close()
    print(f"Entry with Aadhaar number {aadhaar_number} deleted (if existed).")