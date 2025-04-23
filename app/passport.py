import pytesseract, cv2, re

mrz_path = r"C:\Users\shaik\OneDrive\Desktop\eKYC base\passport.png"

# ------------ OCR the image ------------
mrz_img   = cv2.imread(mrz_path)
mrz_text  = pytesseract.image_to_string(
                mrz_img,
                config="--oem 1 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ<0123456789"
            )

# keep only first two MRZ lines, strip blanks
mrz_lines = [l.replace(' ', '') for l in mrz_text.split('\n') if l.strip()][:2]
mrz       = ''.join(mrz_lines)                      # 2 × 44 chars = 88

if len(mrz) < 88:
    raise ValueError("MRZ not read correctly – check the image / crop")

# ------------ split the MRZ ------------
line1, line2 = mrz[:44], mrz[44:]

passport_no  = line1[0:9].replace('<', '')
country_code = line1[10:13]
surname, given = line1[13:].split('<<', 1)
surname      = surname.replace('<', '')
given_name   = given.replace('<', ' ').strip()

nationality  = line2[10:13]
dob          = line2[13:19]     # YYMMDD
sex          = line2[20]
expiry       = line2[21:27]     # YYMMDD

# ------------ show the result ------------
print(f"Passport Number : {passport_no}")
print(f"Country Code    : {country_code}")
print(f"Surname         : {surname}")
print(f"Given Name      : {given_name}")
print(f"Nationality     : {nationality}")
print(f"Date of Birth   : {dob[:2]}-{dob[2:4]}-19{dob[4:]}")   # simple YY→19YY
print(f"Sex             : {sex}")
print(f"Expiry Date     : {expiry[:2]}-{expiry[2:4]}-20{expiry[4:]}")