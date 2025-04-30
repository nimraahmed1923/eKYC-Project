
import sqlite3

def insert_data(data):
    conn = sqlite3.connect("ekyc.db")
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ekyc_data (
            document_type TEXT,
            aadhaar_number TEXT,
            pan_number TEXT,
            passport_number TEXT,
            name TEXT,
            father_name TEXT,
            address TEXT
        )
    """)

    # Delete any existing record with the same unique ID
    if data['Document Type'] == "Aadhaar":
        cursor.execute("DELETE FROM ekyc_data WHERE aadhaar_number = :Aadhaar_Number", {
            "Aadhaar_Number": data['Aadhaar Number']
        })
    elif data['Document Type'] == "PAN":
        cursor.execute("DELETE FROM ekyc_data WHERE pan_number = :PAN_Number", {
            "PAN_Number": data['PAN Number']
        })
    elif data['Document Type'] == "Passport":
        cursor.execute("DELETE FROM ekyc_data WHERE passport_number = :Passport_Number", {
            "Passport_Number": data['Passport Number']
        })

    # Insert new data using named bindings
    cursor.execute("""
        INSERT INTO ekyc_data (
            document_type, aadhaar_number, pan_number, passport_number,
            name, father_name, address
        ) VALUES (
            :Document_Type, :Aadhaar_Number, :PAN_Number, :Passport_Number,
            :Name, :Father_Name, :Address
        )
    """, {
        "Document_Type": data['Document Type'],
        "Aadhaar_Number": data['Aadhaar Number'],
        "PAN_Number": data['PAN Number'],
        "Passport_Number": data['Passport Number'],
        "Name": data['Name'],
        "Father_Name": data['Father Name'],
        "Address": data['Address']
    })

    conn.commit()
    conn.close()

def fetch_all_data():
    conn = sqlite3.connect("ekyc.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM ekyc_data")
    rows = cursor.fetchall()

    conn.close()
    return rows
