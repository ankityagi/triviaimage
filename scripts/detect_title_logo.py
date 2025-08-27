import cv2
import numpy as np
import os
from glob import glob

POSTERS_DIR = './frontend/posters'
OUTPUT_DIR = './frontend/posters_blurred'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Helper function to find the largest text region (likely the title logo)
def detect_title_logo(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Use MSER to detect text regions
    mser = cv2.MSER_create()
    regions, _ = mser.detectRegions(gray)
    mask = np.zeros((gray.shape[0], gray.shape[1]), dtype=np.uint8)
    for p in regions:
        hull = cv2.convexHull(p.reshape(-1, 1, 2))
        cv2.drawContours(mask, [hull], -1, 255, -1)
    # Find contours from mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # Find the largest contour (by area)
    if contours:
        largest = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest)
        return (x, y, w, h)
    return None

# Process all images in the posters directory
for img_path in glob(os.path.join(POSTERS_DIR, '*.jpg')):
    bbox = detect_title_logo(img_path)
    image = cv2.imread(img_path)
    if bbox:
        x, y, w, h = bbox
        # Blur the detected region
        blurred = image.copy()
        roi = blurred[y:y+h, x:x+w]
        roi_blur = cv2.GaussianBlur(roi, (51, 51), 0)
        blurred[y:y+h, x:x+w] = roi_blur
        cv2.imwrite(os.path.join(OUTPUT_DIR, os.path.basename(img_path).replace('.jpg', '_blurred.jpg')), blurred)
        print(f"{os.path.basename(img_path)}: Blurred title logo at {bbox}")
    else:
        print(f"{os.path.basename(img_path)}: No title logo detected")
