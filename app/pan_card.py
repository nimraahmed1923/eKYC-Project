import easyocr
import re

# Initialize EasyOCR reader (English only, no GPU)
reader = easyocr.Reader(['en'], gpu=False)

def extract_document_data(image_path, selected_doc_type):
    try:
        results = reader.readtext(image_path)

        doc_type = selected_doc_type
        aadhaar_number = pan_number = passport_number = name = father_name = address = dob = gender = ""

        # Convert to list of (y_position, text) and sort vertically
        boxes = [(min([pt[1] for pt in box]), text.strip()) for box, text, _ in results]
        boxes.sort()  # Sort by vertical position

        # PAN Card Logic
        if doc_type == "PAN":
            text_full = ' '.join([b[1] for b in boxes])

            # Extract PAN number
            pan_match = re.search(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b", text_full)
            if pan_match:
                pan_number = pan_match.group()

            for i, (_, text) in enumerate(boxes):
                # Extract Name
                if re.search(r"Name", text, re.IGNORECASE) and i + 1 < len(boxes):
                    possible_name = boxes[i + 1][1]
                    if len(possible_name.split()) >= 2 and not re.search(r"Father|नाम|तिथि", possible_name, re.IGNORECASE):
                        name = re.sub(r"[^a-zA-Z\s]", "", possible_name).strip()

                # Extract Father's Name
                if re.search(r"Father", text, re.IGNORECASE) and i + 1 < len(boxes):
                    possible_father = boxes[i + 1][1]
                    if len(possible_father.split()) >= 2 and not re.search(r"Date|Signature", possible_father, re.IGNORECASE):
                        father_name = re.sub(r"[^a-zA-Z\s]", "", possible_father).strip()

                # Extract DOB
                if re.search(r"Date", text, re.IGNORECASE) and i + 1 < len(boxes):
                    dob_match = re.search(r"\d{2}/\d{2}/\d{4}", boxes[i + 1][1])
                    if dob_match:
                        dob = dob_match.group()

        # Fallbacks
        if not pan_number: pan_number = 'AAAAA0000A'
        if not name: name = 'Unknown Name'
        if not father_name: father_name = 'Unknown Father'
        if not dob: dob = '01/01/1990'

        return {
            'Document Type': doc_type,
            'PAN Number': pan_number,
            'Name': name,
            'Father Name': father_name,
            'DOB': dob
        }

    except Exception as e:
        print("EasyOCR Error:", e)
        return None

# ------------------------
# Run & print the output
# ------------------------
if __name__ == "__main__":
    image_path = r"C:\Users\shaik\OneDrive\Desktop\eKYC base\sai_pan.jpeg"  # <- Replace with your actual path
    result = extract_document_data(image_path, "PAN")
    print("\n--- Extracted PAN Card Data ---")
    if result:
        for key, value in result.items():
            print(f"{key}: {value}")
    else:
        print("OCR failed.")