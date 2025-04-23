import easyocr
import re

reader = easyocr.Reader(['en'], gpu=False)

def extract_document_data(image_path, selected_doc_type):
    try:
        results = reader.readtext(image_path)
        doc_type = selected_doc_type
        aadhaar_number = pan_number = passport_number = name = father_name = address = dob = gender = ""
        surname = given_name = place_of_birth = place_of_issue = date_of_issue = date_of_expiry = nationality = ""
        # Get y-position and text sorted top-down
        boxes = [(min([pt[1] for pt in box]), text.strip()) for box, text, _ in results]
        boxes.sort()
        text_full = ' '.join([b[1] for b in boxes])

# === Aadhaar Logic (Final Clean Name Extraction) ===
        if doc_type == "Aadhaar":
            aadhaar_match = re.search(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b", text_full)
            if aadhaar_match:
                aadhaar_number = aadhaar_match.group().replace(" ", "").replace("-", "")

            gov_found = False
            for _, line in boxes:
                clean = line.strip()

                # Skip Hindi/garbage/symbols
                if any(char in clean for char in "!@#$%^&*()[]{}:;<>/\\|1234567890"):
                    continue
                if clean.upper() == clean:  # Skip all-caps (like GOVERNMENT)
                    continue
                if "government of india" in clean.lower():
                    gov_found = True
                    continue

                # Look for name *after* govt heading
                if gov_found and len(clean.split()) >= 2:
                    # Accept if line has mostly lowercase or title case
                    if clean == clean.title() or clean == clean.lower():
                        name = clean
                        break

            # Extract DOB
            for _, line in boxes:
                match = re.search(r"\d{2}[/-]\d{2}[/-]\d{4}", line)
                if match:
                    dob = match.group()
                    break

            # Extract Gender
            for _, line in boxes:
                if re.search(r"\bmale\b|\bpurush\b", line, re.IGNORECASE):
                    gender = "Male"
                elif re.search(r"\bfemale\b|\bnari\b", line, re.IGNORECASE):
                    gender = "Female"

            address = "Not available"

        # === PAN Card Logic (Untouched) ===
        elif doc_type == "PAN":
            pan_index = -1
            for i, (_, text) in enumerate(boxes):
                match = re.search(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b", text)
                if match:
                    pan_number = match.group()
                    pan_index = i
                    break

            if pan_index != -1:
                for i in range(pan_index + 1, len(boxes)):
                    line = boxes[i][1]
                    if re.search(r"[A-Z]{2,}", line) and not re.search(r"\d", line):
                        if len(line.strip().split()) >= 2:
                            name = line.strip()
                            break

            for i, (_, text) in enumerate(boxes):
                if "father" in text.lower():
                    for j in range(i + 1, len(boxes)):
                        line = boxes[j][1]
                        if re.search(r"[A-Z]{2,}", line) and not re.search(r"\d", line):
                            if len(line.strip().split()) >= 2:
                                father_name = line.strip()
                                break
                    break

            for _, line in boxes:
                match = re.search(r"\d{2}/\d{2}/\d{4}", line)
                if match:
                    dob = match.group()
                    break
            address = "Not availabe"

        # === Passport Logic (Untouched) ===
        elif doc_type == "Passport":
            passport_number_pattern = r"\b[A-Z][0-9]{7}\b"
            dob_pattern = r"\d{2}[-/]\d{2}[-/]\d{4}"

            for i, (_, line) in enumerate(boxes):
                # Passport Number
                if not passport_number:
                    match = re.search(passport_number_pattern, line)
                    if match:
                        passport_number = match.group()

                # Nationality and Gender
                if "INDIAN" in line.upper():
                    nationality = "INDIAN"
                if re.search(r"\b[M|F]\b", line):
                    gender = re.search(r"\b[M|F]\b", line).group()

                # Date of Birth
                if not dob:
                    dob_match = re.search(dob_pattern, line)
                    if dob_match:
                        dob = dob_match.group()

                # Place of Birth (comma separated all caps line)
                if ',' in line and line.upper() == line and not re.search(r'\d', line):
                    place_of_birth = line.strip()

                # Place of Issue (usually same format, below Place of Birth)
                if not place_of_issue and place_of_birth and i > 0:
                    next_line = boxes[i + 1][1] if i + 1 < len(boxes) else ''
                    if next_line.upper() == next_line and not re.search(r'\d', next_line):
                        place_of_issue = next_line.strip()

                # Date of Issue & Expiry
                date_matches = re.findall(dob_pattern, line)
                if len(date_matches) == 2:
                    date_of_issue, date_of_expiry = date_matches

            # Given Name & Surname Logic
            for i, (_, line) in enumerate(boxes):
                if "surname" in line.lower():
                    if i + 1 < len(boxes):
                        surname = boxes[i + 1][1].strip()
                if "given" in line.lower():
                    if i + 1 < len(boxes):
                        given_name = boxes[i + 1][1].strip()

            # Assign name as "GIVEN SURNAME"
            name = f"{given_name} {surname}".strip()

        # === Fallbacks ===
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
        print("EasyOCR Error:", e)
        return None