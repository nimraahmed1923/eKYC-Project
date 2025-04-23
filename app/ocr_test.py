import re
import sqlite3
import pytesseract
from PIL import Image

# Optional: Set the Tesseract path (only if it's not in your PATH)
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Step 1: Load the image
image_path = "sample_id.png"  # Make sure this file exists in your working directory
image = Image.open('../sample_id.png')
# Step 2: Convert image to grayscale
gray = image.convert("L")

# Step 3: OCR to extract text
text = pytesseract.image_to_string(gray)
print("Extracted Text:\n", text)

# Step 4: Parse Aadhaar data using regex
aadhaar_data = []
lines = text.split('\n')

for line in lines:
    line = line.strip()
    if 'aadhaar_number' in line.lower():  # Skip header line
        continue

    match = re.match(r"(\d{12}),\s*(fp_\w+),\s*(\w+)", line)
    if match:
        aadhaar_number, fingerprint_id, location = match.groups()
        aadhaar_data.append({
            "aadhaar_number": aadhaar_number,
            "fingerprint_id": fingerprint_id,
            "location": location
        })

# Step 5: Show parsed output
print("\nParsed Aadhaar Data:")
for entry in aadhaar_data:
    print(entry)

# Step 6: Create or open SQLite database
conn = sqlite3.connect("aadhaar_data.db")  # This creates the file if it doesn't exist
cursor = conn.cursor()

# Step 7: Create table if not exists
cursor.execute('''
    CREATE TABLE IF NOT EXISTS aadhaar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        aadhaar_number TEXT,
        fingerprint_id TEXT,
        location TEXT
    )
''')

# Step 8: Insert parsed data into the table
for entry in aadhaar_data:
    cursor.execute('''
        INSERT INTO aadhaar (aadhaar_number, fingerprint_id, location)
        VALUES (?, ?, ?)
    ''', (entry["aadhaar_number"], entry["fingerprint_id"], entry["location"]))

# Step 9: Save and close database
conn.commit()
conn.close()

print("\nData saved successfully to SQLite database (aadhaar_data.db)")