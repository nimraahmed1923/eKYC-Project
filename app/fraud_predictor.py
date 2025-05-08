import joblib
import pandas as pd

# Load model and label encoder
model = joblib.load('fraud_model.pkl')
label_encoder = joblib.load('label_encoder.pkl')

def prepare_input(entry):
    """
    Convert a raw eKYC entry (dictionary) into model input format.
    """
    return pd.DataFrame([{
        'aadhaar_length': len(str(entry.get('aadhaar_number', ''))),
        'pan_length': len(str(entry.get('pan_number', ''))),
        'passport_length': len(str(entry.get('passport_number', ''))),
        'fingerprint_score': entry.get('fingerprint_score', 0)
    }])

def predict_fraud(entry):
    """
    Predict whether the given eKYC entry is Fraud or Genuine.
    """
    X = prepare_input(entry)
    prediction = model.predict(X)[0]
    label = label_encoder.inverse_transform([prediction])[0]
    return label

# Example usage for testing
if __name__ == "__main__":
    sample_entry = {
        'aadhaar_number': '123456789012',
        'pan_number': 'ABCDE1234F',
        'passport_number': '',
        'fingerprint_score': 390
    }

    result = predict_fraud(sample_entry)
    print(f"[PREDICTION] This entry is predicted as: {result}")
