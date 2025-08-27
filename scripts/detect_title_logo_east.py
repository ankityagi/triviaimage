import cv2
import numpy as np
import os
from glob import glob

POSTERS_DIR = '../frontend/posters_raw'
OUTPUT_DIR = '../frontend/posters_blurred_east'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Download the EAST model if not present
EAST_MODEL = 'frozen_east_text_detection.pb'
if not os.path.exists(EAST_MODEL):
    print('Download the EAST model from https://github.com/opencv/opencv_extra/blob/master/testdata/dnn/download_models.py and place frozen_east_text_detection.pb in this folder.')
    exit(1)

def detect_text_east(image_path, min_confidence=0.5):
    print("frfd")
    image = cv2.imread(image_path)
    orig = image.copy()
    (H, W) = image.shape[:2]
    newW, newH = (320, 320)
    rW = W / float(newW)
    rH = H / float(newH)
    image = cv2.resize(image, (newW, newH))
    blob = cv2.dnn.blobFromImage(image, 1.0, (newW, newH), (123.68, 116.78, 103.94), swapRB=True, crop=False)
    net = cv2.dnn.readNet(EAST_MODEL)
    net.setInput(blob)
    (scores, geometry) = net.forward(['feature_fusion/Conv_7/Sigmoid', 'feature_fusion/concat_3'])
    rects = []
    confidences = []
    for y in range(0, scores.shape[2]):
        scoresData = scores[0, 0, y]
        xData0 = geometry[0, 0, y]
        xData1 = geometry[0, 1, y]
        xData2 = geometry[0, 2, y]
        xData3 = geometry[0, 3, y]
        anglesData = geometry[0, 4, y]
        for x in range(0, scores.shape[3]):
            if scoresData[x] < min_confidence:
                continue
            offsetX, offsetY = x * 4.0, y * 4.0
            angle = anglesData[x]
            cos = np.cos(angle)
            sin = np.sin(angle)
            h = xData0[x] + xData2[x]
            w = xData1[x] + xData3[x]
            endX = int(offsetX + (cos * xData1[x]) + (sin * xData2[x]))
            endY = int(offsetY - (sin * xData1[x]) + (cos * xData2[x]))
            startX = int(endX - w)
            startY = int(endY - h)
            rects.append([startX, startY, w, h])
            confidences.append(float(scoresData[x]))
    # Use NMSBoxes for axis-aligned rectangles
    indices = cv2.dnn.NMSBoxes(rects, confidences, min_confidence, 0.4)
    results = []
    if len(indices) > 0:
        for i in indices.flatten():
            (startX, startY, w, h) = rects[i]
            endX = startX + w
            endY = startY + h
            startX = int(startX * rW)
            startY = int(startY * rH)
            endX = int(endX * rW)
            endY = int(endY * rH)
            results.append((startX, startY, endX, endY))
    return results, orig

print("starting to blur")
print(os.path.join(POSTERS_DIR, '*.jpg'))
for img_path in glob(os.path.join(POSTERS_DIR, '*.jpg')):
    print("starting to blur")
    boxes, image = detect_text_east(img_path)
    blurred = image.copy()
    found = False
    
    for (startX, startY, endX, endY) in boxes:
        # Blur each detected text region
        roi = blurred[max(0, startY):min(blurred.shape[0], endY), max(0, startX):min(blurred.shape[1], endX)]
        if roi.size > 0:
            roi_blur = cv2.GaussianBlur(roi, (99, 99), 0)
            blurred[max(0, startY):min(blurred.shape[0], endY), max(0, startX):min(blurred.shape[1], endX)] = roi_blur
            found = True
    out_path = os.path.join(OUTPUT_DIR, os.path.basename(img_path).replace('.jpg', '_blurred.jpg'))
    cv2.imwrite(out_path, blurred)
    print(f"{os.path.basename(img_path)}: {'Blurred' if found else 'No text detected'}")
