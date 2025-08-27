import cv2
import pytesseract
import numpy as np
import os
from glob import glob

POSTERS_DIR = '../frontend/posters'
OUTPUT_DIR = '../frontend/posters_blurred_ocr'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# You may need to set the tesseract_cmd path if not in PATH
# pytesseract.pytesseract.tesseract_cmd = r'/usr/local/bin/tesseract'

def detect_title_logo_ocr(image_path):
    print(f"[detect_title_logo_ocr] Processing {img_path}")
    image = cv2.imread(image_path)
    # Resize image to max width 600px for faster OCR
    h, w = image.shape[:2]
    if w > 600:
        new_h = int(h * 600 / w)
        image = cv2.resize(image, (600, new_h))
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    print(f"[detect_title_logo_ocr] Before Pytesseract {img_path}")
    try:
        data = pytesseract.image_to_data(
            gray,
            output_type=pytesseract.Output.DICT,
            config='--psm 12'
        )
    except RuntimeError:
        print(f"[detect_title_logo_ocr] Timeout or error for {img_path}")
        return [], image
    print(f"[detect_title_logo_ocr] After Pytesseract {img_path}")
    n_boxes = len(data['level'])
    title_boxes = []
    for i in range(n_boxes):
        text = data['text'][i].strip()
        # Heuristic: Only consider boxes with at least 2 characters
        if len(text) >= 2:
            (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
            title_boxes.append((x, y, w, h))
    return title_boxes, image

for img_path in glob(os.path.join(POSTERS_DIR, '*.jpg')):
    print(f"[outside] Processing {img_path}")
    boxes, image = detect_title_logo_ocr(img_path)
    blurred = image.copy()
    found = False
    for (x, y, w, h) in boxes:
        roi = blurred[y:y+h, x:x+w]
        if roi.size > 0:
            roi_blur = cv2.GaussianBlur(roi, (51, 51), 0)
            blurred[y:y+h, x:x+w] = roi_blur
            found = True
    out_path = os.path.join(OUTPUT_DIR, os.path.basename(img_path).replace('.jpg', '_blurred.jpg'))
    cv2.imwrite(out_path, blurred)
    print(f"{os.path.basename(img_path)}: {'Blurred' if found else 'No title text detected'}")
