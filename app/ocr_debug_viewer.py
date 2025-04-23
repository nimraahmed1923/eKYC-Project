import easyocr
import cv2
import os

# ===== CONFIG =====
image_path = "C:\\Users\\shaik\\OneDrive\\Desktop\\eKYC base\\anik_aadhaar.jpg"  # Your PAN card image path
output_path = "debug_pan_output.jpg"  # Where to save annotated image
# ===================

reader = easyocr.Reader(['en'])

results = reader.readtext(image_path)
image = cv2.imread(image_path)

print("\n=== OCR LINES DETECTED ===")
for i, (bbox, text, conf) in enumerate(results):
    print(f"[LINE {i}] → {text}")
    # Draw the boxes
    (top_left, top_right, bottom_right, bottom_left) = bbox
    top_left = tuple(map(int, top_left))
    bottom_right = tuple(map(int, bottom_right))
    cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)
    cv2.putText(image, f"{i}", top_left, cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

print("\n=== Full Raw Text ===")
all_text = "\n".join([res[1] for res in results])
print(all_text)

# Save image with bounding boxes
cv2.imwrite(output_path, image)
print(f"\nAnnotated image saved to: {os.path.abspath(output_path)}")