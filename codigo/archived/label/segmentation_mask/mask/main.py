import os
import cv2
import xml.etree.ElementTree as ET
import numpy as np

os.makedirs("x", exist_ok=True)
os.makedirs("y", exist_ok=True)

tree = ET.parse('./annotations.xml')
root = tree.getroot()

def apply_mask(image, area_coords, head_coords, eye_coords):
    mask = cv2.rectangle(
        np.zeros_like(image), 
        (int(float(area_coords['xtl'])), int(float(area_coords['ytl']))),
        (int(float(area_coords['xbr'])), int(float(area_coords['ybr']))),
        (0, 0, 0), -1
    )
    if head_coords:
        mask = cv2.rectangle(
            mask,
            (int(float(head_coords['xtl'])), int(float(head_coords['ytl']))),
            (int(float(head_coords['xbr'])), int(float(head_coords['ybr']))),
            (255, 255, 255), -1
        )
    if eye_coords:
        for eye in eye_coords:
            mask = cv2.rectangle(
                mask,
                (int(float(eye['xtl'])), int(float(eye['ytl']))),
                (int(float(eye['xbr'])), int(float(eye['ybr']))),
                (0, 0, 255), -1
            )
    return mask

for image in root.findall('image'):
    image_name = image.get('name')
    
    base_filename = image_name.replace("../frames/output/", "")
    base_filename = os.path.splitext(base_filename)[0] 
    
    original_image = cv2.imread(image_name)
    
    area_boxes = []
    head_boxes = []
    eye_boxes = []
    
    for box in image.findall('box'):
        label = box.get('label')
        coords = {
            'xtl': box.get('xtl'),
            'ytl': box.get('ytl'),
            'xbr': box.get('xbr'),
            'ybr': box.get('ybr')
        }
        
        if label == 'area':
            area_boxes.append(coords)
        elif label == 'cabeca':
            head_boxes.append(coords)
        elif label == 'olho':
            eye_boxes.append(coords)
    
    for j, area_box in enumerate(area_boxes, start=1):
        
        x_filename = f"{base_filename}_{j}_x.png"
        y_filename = f"{base_filename}_{j}_y.png"
        
        crop_img = original_image[
            int(float(area_box['ytl'])):int(float(area_box['ybr'])),
            int(float(area_box['xtl'])):int(float(area_box['xbr']))
        ]
        
        resized_crop_img = cv2.resize(crop_img, (128, 128))
        cv2.imwrite(os.path.join("x", x_filename), resized_crop_img)
        
        relevant_head_box = None
        relevant_eye_boxes = []

        for head_box in head_boxes:
            if (float(head_box['xtl']) >= float(area_box['xtl']) and
                float(head_box['xbr']) <= float(area_box['xbr']) and
                float(head_box['ytl']) >= float(area_box['ytl']) and
                float(head_box['ybr']) <= float(area_box['ybr'])):
                relevant_head_box = head_box
                break

        for eye_box in eye_boxes:
            if (float(eye_box['xtl']) >= float(area_box['xtl']) and
                float(eye_box['xbr']) <= float(area_box['xbr']) and
                float(eye_box['ytl']) >= float(area_box['ytl']) and
                float(eye_box['ybr']) <= float(area_box['ybr'])):
                relevant_eye_boxes.append(eye_box)

        mask = apply_mask(original_image, area_box, relevant_head_box, relevant_eye_boxes)
        masked_image = cv2.addWeighted(mask, 1, original_image, 0, 0)
        cropped_masked_image = masked_image[
            int(float(area_box['ytl'])):int(float(area_box['ybr'])),
            int(float(area_box['xtl'])):int(float(area_box['xbr']))
        ]
        
        resized_masked_image = cv2.resize(cropped_masked_image, (128, 128))
        cv2.imwrite(os.path.join("y", y_filename), resized_masked_image)
