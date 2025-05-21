import os
import sys
import django
import sqlite3

# Fix sys.path to include your Django project folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'ekyc_project')))





# Set up Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ekyc_project.settings")

django.setup()

from dashboard_v2.models import EkycData

# Connect to the SQLite database
conn = sqlite3.connect("ekyc_database.db")
cursor = conn.cursor()

# Fetch data from existing DB
cursor.execute("SELECT * FROM ekyc_data")
rows = cursor.fetchall()

# Get column names
columns = [desc[0] for desc in cursor.description]
conn.close()

# Insert into Django model
for row in rows:
    data = dict(zip(columns, row))

    EkycData.objects.create(
        document_type=data.get('document_type', ''),
        name=data.get('name', ''),
        father_name=data.get('father_name', ''),
        dob=data.get('dob', ''),
        gender=data.get('gender', ''),
        aadhaar_number=data.get('aadhaar_number', ''),
        pan_number=data.get('pan_number', ''),
        passport_number=data.get('passport_number', ''),
        nationality=data.get('nationality', ''),
        place_of_birth=data.get('place_of_birth', ''),
        place_of_issue=data.get('place_of_issue', ''),
        date_of_issue=data.get('date_of_issue', ''),
        date_of_expiry=data.get('date_of_expiry', ''),
        status=data.get('status', 'Clear'),
        timestamp=data.get('timestamp')
    )

print(f"✅ Imported {len(rows)} records successfully.")
