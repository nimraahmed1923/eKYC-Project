import pytesseract
import cv2

# Path to your image
image_path = "../dataset/documents/sample_id.png"

# If Tesseract is installed in a custom path, specify it below
# (example for Windows)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Load the image
image = cv2.imread(image_path)

# Convert image to grayscale (helps OCR accuracy)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Apply OCR
text = pytesseract.image_to_string(gray)

print("=== Extracted Text ===")
print(text)