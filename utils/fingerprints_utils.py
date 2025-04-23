import cv2
import numpy as np

def preprocess_fingerprint(image_path):
    print(f"[DEBUG] Loading image from path: {image_path}")  # Add this!
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"Image not found or unreadable: {image_path}")
    blur = cv2.GaussianBlur(img, (5, 5), 0)
    return blur
def compare_fingerprints(img1_path, img2_path):
    img1 = preprocess_fingerprint(img1_path)
    img2 = preprocess_fingerprint(img2_path)

    orb = cv2.ORB_create()
    kp1, des1 = orb.detectAndCompute(img1, None)
    kp2, des2 = orb.detectAndCompute(img2, None)

    if des1 is None or des2 is None:
        return 0

    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2)

    score = len(matches)
    return score