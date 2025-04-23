import cv2
import pytesseract
import re
import numpy as np
import sys
import os

# Add parent directory to system path to import from utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.ocr_utils import extract_ocr_data  # EasyOCR-based extraction

# Optional: if tesseract is not in PATH, uncomment and set the path
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def run_ocr(image_path):
    """
    Runs the improved OCR extraction on the given image using EasyOCR and standardization logic.
    """
    try:
        extracted_data = extract_ocr_data(image_path)
        print("OCR Extraction Successful!")
        print(extracted_data)
        return extracted_data
    except Exception as e:
        print("OCR Extraction Failed:", str(e))
        return {"error": str(e)}

def extract_document_data(image_path, selected_doc_type):
    """
    Compatible legacy OCR method for GUI use until all transitions are complete.
    Calls EasyOCR-based extraction as fallback.
    """
    try:
        # Preprocess image
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise FileNotFoundError("Image not found.")

        img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        text = pytesseract.image_to_string(img, lang='eng+hin')
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        full_text = ' '.join(lines)

        doc_type = selected_doc_type
        aadhaar_number = pan_number = passport_number = name = father_name = address = dob = gender = ""

        # Aadhaar Card Logic
        if doc_type == "Aadhaar":
            aadhaar_match = re.search(r"\b\d{4}\s\d{4}\s\d{4}\b", full_text)
            if aadhaar_match:
                aadhaar_number = aadhaar_match.group().replace(" ", "")

            for line in lines:
                if re.search(r'\b(Name|नाम)\b', line, re.IGNORECASE):
                    possible_name = re.sub(r"(Name|नाम|:)", "", line, flags=re.IGNORECASE).strip()
                    if len(possible_name.split()) >= 2:
                        name = possible_name
                        break

            if not name:
                possible_names = [line for line in lines if len(line.split()) >= 2 and not re.search(r"\d", line)]
                name = possible_names[0] if possible_names else "Unknown Name"

            # DOB
            dob_match = re.search(r"\b\d{2}[-./]\d{2}[-./]\d{4}\b", full_text)
            if dob_match:
                dob = dob_match.group()

            # Gender detection
            for line in lines:
                if re.search(r"\bmale\b|\bpurush\b", line, re.IGNORECASE):
                    gender = "Male"
                    break
                elif re.search(r"\bfemale\b|\bnari\b", line, re.IGNORECASE):
                    gender = "Female"
                    break

            address = ' '.join(lines[2:]) if len(lines) > 2 else 'Unknown Address'

        # PAN Card Logic
        elif doc_type == "PAN":
            pan_match = re.search(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b", full_text)
            if pan_match:
                pan_number = pan_match.group()

            # Look for DOB
            dob_keywords = ['DOB', 'Date of Birth', 'Birth']
            for line in lines:
                if any(keyword.lower() in line.lower() for keyword in dob_keywords):
                    dob_match = re.search(r"\d{2}/\d{2}/\d{4}", line)
                    if dob_match:
                        dob = dob_match.group()
                        break

            # Name and Father’s Name above DOB
            if dob:
                for i, line in enumerate(lines):
                    if dob in line:
                        if i >= 2:
                            name_candidate = lines[i - 2]
                            father_candidate = lines[i - 1]
                            if name_candidate and not re.search(r'\d', name_candidate):
                                name = name_candidate
                            if father_candidate and not re.search(r'\d', father_candidate):
                                father_name = father_candidate
                        break

        # Passport Logic
        elif doc_type == "Passport":
            passport_match = re.search(r"\b[A-Z][0-9]{7}\b", full_text)
            if passport_match:
                passport_number = passport_match.group()

            dob_match = re.search(r"\b\d{2}[-./]\d{2}[-./]\d{4}\b", full_text)
            if dob_match:
                dob = dob_match.group()

            name_candidates = [line for line in lines if len(line.split()) >= 2 and not re.search(r"\d", line)]
            if name_candidates:
                name = name_candidates[0]

            address = ' '.join(lines[2:]) if len(lines) > 2 else 'Unknown Address'

        # Fallbacks
        if not aadhaar_number: aadhaar_number = '000000000000'
        if not pan_number: pan_number = 'AAAAA0000A'
        if not passport_number: passport_number = 'A0000000'
        if not name: name = 'Unknown Name'
        if not father_name: father_name = 'Unknown Father'
        if not address: address = 'Unknown Address'
        if not dob: dob = '01/01/1990'
        if not gender: gender = 'Unknown'

        return {
            'Document Type': doc_type,
            'Aadhaar Number': aadhaar_number,
            'PAN Number': pan_number,
            'Passport Number': passport_number,
            'Name': name,
            'Father Name': father_name,
            'DOB': dob,
            'Gender': gender,
            'Address': address
        }

    except Exception as e:
        print("OCR Extraction Error:", str(e))
        return None