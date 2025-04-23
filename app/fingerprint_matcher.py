import os
import sys

# Add the project root to the system path for proper imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.fingerprints_utils import compare_fingerprints

def find_best_match(test_fingerprint_path, dataset_path):
    """
    Compares the test fingerprint with all fingerprints in the dataset folder
    and returns the filename of the best match along with the match score.
    """
    best_match = None
    best_score = 0

    # Loop through all fingerprint images in the dataset directory
    for filename in os.listdir(dataset_path):
        if filename.lower().endswith(".bmp"):
            candidate_path = os.path.join(dataset_path, filename)

            try:
                score = compare_fingerprints(test_fingerprint_path, candidate_path)

                if score > best_score:
                    best_score = score
                    best_match = filename

            except Exception as e:
                print(f"[ERROR] Failed to compare with {filename}: {e}")

    return best_match, best_score