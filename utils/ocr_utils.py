import re

def extract_ocr_data(text: str) -> dict:
    text = text.strip()
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    full_text = " ".join(lines).lower()

    result = {
        'Document Type': 'Unknown',
        'PAN Number': None,
        'Aadhaar Number': None,
        'Name': None,
        'Father Name': None,
        'DOB': None,
        'Gender': None,
        'Address': 'Unknown Address'
    }

    # Detect Document Type
    if 'income tax department' in full_text or re.search(r'[A-Z]{5}[0-9]{4}[A-Z]', text):
        result['Document Type'] = 'PAN'
    elif 'government of india' in full_text or re.search(r'\b\d{4}\s\d{4}\s\d{4}\b', text):
        result['Document Type'] = 'Aadhaar'

    # PAN Number (10-character pattern)
    pan_match = re.search(r'\b([A-Z]{5}[0-9]{4}[A-Z])\b', text)
    if pan_match:
        result['PAN Number'] = pan_match.group(1)

    # Aadhaar Number (12-digit pattern)
    aadhaar_match = re.search(r'\b\d{4}\s\d{4}\s\d{4}\b', text)
    if aadhaar_match:
        result['Aadhaar Number'] = aadhaar_match.group()

    # Name
    for line in lines:
        if re.search(r"\b(name|नाम)\b", line, re.IGNORECASE) and not re.search(r"father", line, re.IGNORECASE):
            name = line.split(':')[-1] if ':' in line else line.split('/')[-1]
            result['Name'] = name.strip().title()
            break

    # Father's Name
    for line in lines:
        if re.search(r"father['’]?[s ]?name|पिता का नाम", line, re.IGNORECASE):
            father = line.split(':')[-1] if ':' in line else line.split('/')[-1]
            result['Father Name'] = father.strip().title()
            break

    # DOB
    dob_patterns = [
        r'\b\d{2}[/-]\d{2}[/-]\d{4}\b',  # 01/01/2000 or 01-01-2000
        r'\d{4}[/-]\d{2}[/-]\d{2}',      # 2000-01-01
    ]
    for line in lines:
        if any(k in line.lower() for k in ['dob', 'date of birth', 'जन्म', 'जन्म तिथि']):
            for pattern in dob_patterns:
                match = re.search(pattern, line)
                if match:
                    result['DOB'] = match.group()
                    break
        if result['DOB']:
            break
    if not result['DOB']:
        for pattern in dob_patterns:
            match = re.search(pattern, full_text)
            if match:
                result['DOB'] = match.group()
                break

    # Gender
    gender_keywords = {
        'male': 'Male', 'पुरुष': 'Male',
        'female': 'Female', 'स्त्री': 'Female'
    }
    for word in full_text.split():
        word_clean = word.lower().strip("/:-")
        if word_clean in gender_keywords:
            result['Gender'] = gender_keywords[word_clean]
            break

    return result