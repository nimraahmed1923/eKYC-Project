import sqlite3

def init_db():
    """Initialize the database and create the eKYC table if it doesn't exist."""
    conn = sqlite3.connect('ekyc_database.db')
    cursor = conn.cursor()

    # Ensure the table exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ekyc_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_type TEXT,
            name TEXT,
            father_name TEXT,
            dob TEXT,
            gender TEXT,
            aadhaar_number TEXT,
            pan_number TEXT,
            passport_number TEXT,
            nationality TEXT,
            place_of_birth TEXT,
            place_of_issue TEXT,
            date_of_issue TEXT,
            date_of_expiry TEXT,
            status TEXT,
            fingerprint_score REAL,  -- ✅ NEW COLUMN
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Ensure fingerprint_score column exists (for older DBs)
    try:
        cursor.execute("SELECT fingerprint_score FROM ekyc_data LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE ekyc_data ADD COLUMN fingerprint_score REAL")

    conn.commit()
    conn.close()

def insert_data(data, fingerprint_score=None):
    """Insert extracted data into the database with optional fingerprint score."""
    conn = sqlite3.connect('ekyc_database.db')
    cursor = conn.cursor()
    
    db_data = {
        'document_type': data.get('Document Type', ''),
        'name': data.get('Name', '') or data.get('Given Name', '') or data.get('Surname', ''),
        'father_name': data.get('Father Name', ''),
        'dob': data.get('DOB', ''),
        'gender': data.get('Gender', ''),
        'aadhaar_number': data.get('Aadhaar Number', ''),
        'pan_number': data.get('PAN Number', ''),
        'passport_number': data.get('Passport Number', ''),
        'nationality': data.get('Nationality', ''),
        'place_of_birth': data.get('Place of Birth', ''),
        'place_of_issue': data.get('Place of Issue', ''),
        'date_of_issue': data.get('Date of Issue', ''),
        'date_of_expiry': data.get('Date of Expiry', ''),
        'status': 'Suspicious' if data.get('status', 'Clear') == 'Suspicious' else 'Clear',
        'fingerprint_score': fingerprint_score  # ✅ Add score if provided
    }

    cursor.execute('''
        INSERT INTO ekyc_data (
            document_type, name, father_name, dob, gender, aadhaar_number, pan_number,
            passport_number, nationality, place_of_birth, place_of_issue, date_of_issue,
            date_of_expiry, status, fingerprint_score
        ) VALUES (
            :document_type, :name, :father_name, :dob, :gender, :aadhaar_number, :pan_number,
            :passport_number, :nationality, :place_of_birth, :place_of_issue, :date_of_issue,
            :date_of_expiry, :status, :fingerprint_score
        )
    ''', db_data)

    conn.commit()
    conn.close()

def fetch_all_data():
    """Fetch all records from the database."""
    conn = sqlite3.connect('ekyc_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM ekyc_data ORDER BY timestamp DESC')
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_user_by_id(user_id):
    conn = sqlite3.connect("ekyc_database.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ekyc_data WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

# ✅ Initialize when module is imported
init_db()