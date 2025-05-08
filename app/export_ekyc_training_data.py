import sqlite3
import csv
import random
import os

def fetch_ekyc_data(db_path='ekyc_database.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ekyc_data")
    columns = [desc[0] for desc in cursor.description]
    data = [dict(zip(columns, row)) for row in cursor.fetchall()]
    conn.close()
    return data

def simulate_fingerprint_score(entry):
    """
    Simulate fingerprint match score based on how complete the entry is.
    In your real app, you can fetch actual fingerprint scores.
    """
    base = 300 + random.randint(0, 150)
    penalty = sum(1 for key in ['aadhaar_number', 'pan_number', 'passport_number'] if not entry.get(key))
    return base - (penalty * 50)

def assign_fraud_label(entry):
    """
    For now, randomly assign fraud or genuine.
    Later, we will train AI to predict this.
    """
    return random.choice(['Fraud', 'Genuine'])

def export_to_csv(data, output_path='ekyc_training_data.csv'):
    if not data:
        print("[WARNING] No data to export.")
        return

    # Prepare fields
    fieldnames = list(data[0].keys()) + ['fingerprint_score', 'fraud_label']

    with open(output_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for entry in data:
            entry['fingerprint_score'] = simulate_fingerprint_score(entry)
            entry['fraud_label'] = assign_fraud_label(entry)
            writer.writerow(entry)

    print(f"[INFO] Data exported successfully to '{output_path}'")

# Main execution
if __name__ == "__main__":
    data = fetch_ekyc_data()
    export_to_csv(data)
