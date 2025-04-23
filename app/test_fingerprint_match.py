import os
from fingerprint_matcher import find_best_match

# Use correct relative paths
test_fingerprint = os.path.join("test_fingerprints", "test_2.bmp")
dataset_path = os.path.join("dataset_FVC2000_DB4_B", "dataset", "train_data")

# Make sure test fingerprint file exists
if not os.path.exists(test_fingerprint):
    raise FileNotFoundError(f"Test fingerprint not found at: {test_fingerprint}")

best_match, score = find_best_match(test_fingerprint, dataset_path)

# Threshold to decide a good match
MATCH_THRESHOLD = 15

if best_match and score >= MATCH_THRESHOLD:
    print(f"Best Match: {best_match} with score {score}")
else:
    print("No strong match found.")