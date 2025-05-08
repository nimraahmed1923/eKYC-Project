import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import LabelEncoder
import joblib

def load_data(csv_path='ekyc_training_data.csv'):
    return pd.read_csv(csv_path)

def preprocess_data(df):
    # Select relevant features
    features = ['aadhaar_number', 'pan_number', 'passport_number', 'fingerprint_score']
    df = df[features + ['fraud_label']]

    # Convert to string and calculate lengths
    df['aadhaar_length'] = df['aadhaar_number'].astype(str).fillna('').apply(len)
    df['pan_length'] = df['pan_number'].astype(str).fillna('').apply(len)
    df['passport_length'] = df['passport_number'].astype(str).fillna('').apply(len)

    # Replace missing fingerprint scores with 0
    df['fingerprint_score'] = df['fingerprint_score'].fillna(0)

    # Final feature set
    X = df[['aadhaar_length', 'pan_length', 'passport_length', 'fingerprint_score']]

    # Encode fraud label
    le = LabelEncoder()
    y = le.fit_transform(df['fraud_label'])  # 0 = Fraud, 1 = Genuine

    return X, y, le


def train_model(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    print("[INFO] Model Evaluation:")
    print(classification_report(y_test, y_pred, target_names=["Fraud", "Genuine"]))
    print(f"[INFO] Accuracy: {accuracy_score(y_test, y_pred):.2f}")

    return model

def save_model(model, encoder, model_path='fraud_model.pkl', label_path='label_encoder.pkl'):
    joblib.dump(model, model_path)
    joblib.dump(encoder, label_path)
    print(f"[INFO] Model saved to {model_path}")
    print(f"[INFO] Label encoder saved to {label_path}")

# === Main Execution ===
if __name__ == "__main__":
    print("[INFO] Loading data...")
    df = load_data()

    print("[INFO] Preprocessing data...")
    X, y, label_encoder = preprocess_data(df)

    print("[INFO] Training model...")
    model = train_model(X, y)

    print("[INFO] Saving model...")
    save_model(model, label_encoder)
