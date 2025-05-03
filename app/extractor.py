import easyocr
import re
from PIL import Image

reader = easyocr.Reader(['en'], gpu=False)

def format_mrz_date(date_str):
    try:
        year = int(date_str[:2])
        full_year = "19" + date_str[:2] if year > 30 else "20" + date_str[:2]
        return f"{date_str[4:6]}/{date_str[2:4]}/{full_year}"
    except:
        return ""

def extract_document_data(image_path, selected_doc_type):
    try:
        results = reader.readtext(image_path)
        doc_type = selected_doc_type

        # Initial values
        aadhaar_number = pan_number = passport_number = name = father_name = address = dob = gender = ""
        surname = given_name = place_of_birth = place_of_issue = date_of_issue = date_of_expiry = nationality = ""

        # Combine lines and sort by vertical position
        boxes = [(min([pt[1] for pt in box]), text.strip()) for box, text, _ in results]
        boxes.sort()
        text_lines = [b[1] for b in boxes]
        text_full = ' '.join(text_lines).upper()

        # === Aadhaar Logic ===
        if doc_type == "Aadhaar":
            aadhaar_match = re.search(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b", text_full)
            if aadhaar_match:
                aadhaar_number = aadhaar_match.group().replace(" ", "").replace("-", "")

            # Extract name
            gov_found = False
            for line in text_lines:
                clean = line.strip()
                if any(char.isdigit() for char in clean) or clean.isupper():
                    continue
                if "government of india" in clean.lower():
                    gov_found = True
                    continue
                if gov_found and len(clean.split()) >= 2:
                    if clean == clean.title() or clean == clean.lower():
                        name = clean.title()
                        break

            for line in text_lines:
                match = re.search(r"\d{2}[/-]\d{2}[/-]\d{4}", line)
                if match:
                    dob = match.group()
                    break

            for line in text_lines:
                if re.search(r"\bmale\b|\bpurush\b", line, re.IGNORECASE):
                    gender = "Male"
                elif re.search(r"\bfemale\b|\bnari\b", line, re.IGNORECASE):
                    gender = "Female"

            address = "Not available"

        # === PAN Logic ===
        elif doc_type == "PAN":
            for i, line in enumerate(text_lines):
                match = re.search(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b", line)
                if match:
                    pan_number = match.group()
                    for j in range(i + 1, len(text_lines)):
                        name_line = text_lines[j]
                        if re.search(r"^[A-Z ]+$", name_line) and not re.search(r"\d", name_line):
                            if len(name_line.strip().split()) >= 2:
                                name = name_line.title().strip()
                                break
                    break

            for i, line in enumerate(text_lines):
                if "father" in line.lower():
                    for j in range(i + 1, len(text_lines)):
                        fline = text_lines[j]
                        if re.search(r"^[A-Z ]+$", fline) and not re.search(r"\d", fline):
                            if len(fline.strip().split()) >= 2:
                                father_name = fline.title().strip()
                                break
                    break

            for line in text_lines:
                match = re.search(r"\d{2}/\d{2}/\d{4}", line)
                if match:
                    dob = match.group()
                    break
            address = "Not available"

        # === Passport Logic ===
        elif doc_type == "Passport":
            mrz_lines = [line.replace(" ", "") for line in text_lines if "<<" in line and len(line.replace(" ", "")) >= 40]

            if len(mrz_lines) >= 2:
                mrz1 = mrz_lines[-2]
                mrz2 = mrz_lines[-1]

                try:
                    passport_number = mrz2[0:9].replace("<", "")
                    nationality = mrz2[10:13].replace("<", "")
                    dob_raw = mrz2[13:19]
                    gender_code = mrz2[20]
                    expiry_raw = mrz2[21:27]

                    dob = format_mrz_date(dob_raw)
                    date_of_expiry = format_mrz_date(expiry_raw)
                    gender = {"M": "Male", "F": "Female"}.get(gender_code.upper(), "Unknown")

                    name_parts = mrz1[5:].split("<<")
                    surname = name_parts[0].replace("<", " ").strip().title()
                    given_name = name_parts[1].replace("<", " ").strip().title() if len(name_parts) > 1 else ""
                    name = f"{given_name} {surname}".strip()
                except Exception as parse_error:
                    print("Error parsing MRZ:", parse_error)

            # Fallback date parsing
            date_pattern = r"\d{2}[-/]\d{2}[-/]\d{4}"
            for line in text_lines:
                match = re.findall(date_pattern, line)
                if len(match) >= 2:
                    date_of_issue, date_of_expiry = match[:2]
                    break
                elif not dob:
                    dob_match = re.search(date_pattern, line)
                    if dob_match:
                        dob = dob_match.group()

        # === Fallback Defaults ===
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
            'Given Name': given_name,
            'Surname': surname,
            'DOB': dob,
            'Gender': gender,
            'Nationality': nationality,
            'Date of Issue': date_of_issue,
            'Date of Expiry': date_of_expiry,
            'Father Name': father_name,
            'Address': address
        }

    except Exception as e:
        print("OCR Extraction Error:", e)
        return None