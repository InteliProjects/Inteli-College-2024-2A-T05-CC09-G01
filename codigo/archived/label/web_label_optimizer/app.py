from flask import Flask, render_template, request, jsonify, send_from_directory
from PIL import Image
import os
import cv2
import numpy as np
import base64
from PIL import Image, ImageDraw

app = Flask(__name__)
UPLOAD_FOLDER = 'files/uploads'
PROCESSED_FOLDER = 'files/processed'
FRAMES_FOLDER = 'files/frames'
SEGMENTED_FOLDER = 'files/segmented'
X_FOLDER = 'files/x'
Y_FOLDER = 'files/y'

for folder in [UPLOAD_FOLDER, PROCESSED_FOLDER, FRAMES_FOLDER, SEGMENTED_FOLDER, X_FOLDER, Y_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/processed/<path:filename>')
def processed_files(filename):
    return send_from_directory(PROCESSED_FOLDER, filename)

@app.route('/get_image_stats', methods=['GET'])
def get_image_stats():
    total_images = len([f for f in os.listdir(FRAMES_FOLDER) if f.endswith(('.png', '.jpg', '.jpeg'))])
    processed_images = len([f for f in os.listdir(PROCESSED_FOLDER) if f.endswith(('.png', '.jpg', '.jpeg'))])
    
    return jsonify({
        "total_images": total_images,
        "processed_images": processed_images
    })

@app.route('/apply_mask', methods=['POST'])
def apply_mask():
    data = request.json
    filename = data.get('filename')
    rect_blue = data.get('rectBlue')
    rect1 = data.get('rect1')
    rect2 = data.get('rect2')

    if not all([filename, rect_blue, rect1, rect2]):
        return jsonify({"message": "Missing required data"}), 400

    # Load the original image
    filepath = os.path.join(PROCESSED_FOLDER, filename)
    img = cv2.imread(filepath)

    if img is None:
        return jsonify({"message": "Image not found."}), 400

    # Get image dimensions
    img_height, img_width = img.shape[:2]

    # Function to transform coordinates
    def transform_coords(rect, img_width, img_height):
        return {
            'x': int(rect['x'] * img_width),
            'y': int(rect['y'] * img_height),
            'width': int(rect['width'] * img_width),
            'height': int(rect['height'] * img_height)
        }

    # Transform coordinates
    rect_blue = transform_coords(rect_blue, img_width, img_height)
    rect1 = transform_coords(rect1, img_width, img_height)
    rect2 = transform_coords(rect2, img_width, img_height)

    # Create a mask image
    mask = np.zeros(img.shape[:2], dtype=np.uint8)

    # Draw blue rectangle (white in mask)
    cv2.rectangle(mask, (rect_blue['x'], rect_blue['y']), 
                  (rect_blue['x'] + rect_blue['width'], rect_blue['y'] + rect_blue['height']), 255, -1)

    # Draw red rectangles
    for rect in [rect1, rect2]:
        cv2.rectangle(mask, (rect['x'], rect['y']), 
                      (rect['x'] + rect['width'], rect['y'] + rect['height']), 128, -1)

    # Create the output image
    output = np.zeros_like(img)
    output[mask == 255] = [255, 255, 255]  # White for blue rectangle area
    output[mask == 128] = [0, 0, 255]      # Red for red rectangles areas
    output[mask == 0] = [0, 0, 0]          # Black for the rest

    # Save the masked image in 'files/y'
    output_filename = f"{os.path.splitext(filename)[0]}_y.png"
    output_path_y = os.path.join('files/y', output_filename)
    cv2.imwrite(output_path_y, output)

    # Copy the original image to 'files/x'
    output_path_x = os.path.join('files/x', filename)
    cv2.imwrite(output_path_x, img)

    return jsonify({"message": "Mask applied successfully!", "output": output_filename})

@app.route('/segmented/<path:filename>')
def segmented_files(filename):
    return send_from_directory(SEGMENTED_FOLDER, filename)

@app.route('/upload_video', methods=['POST'])
def upload_video():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        filename = file.filename
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Get video duration
        cap = cv2.VideoCapture(filepath)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps
        cap.release()
        
        return jsonify({"filename": filename, "duration": duration})

@app.route('/fragment_video', methods=['POST'])
def fragment_video():
    data = request.json
    filename = data['filename']
    frames_per_second = int(data['frames_per_second'])
    frame_size = int(data['frame_size']) - 3
    start_time = data['start_time']
    end_time = data['end_time']

    filepath = os.path.join(UPLOAD_FOLDER, filename)
    cap = cv2.VideoCapture(filepath)
    video_fps = cap.get(cv2.CAP_PROP_FPS)

    start_frame = int(float(start_time) * video_fps)
    end_frame = int(float(end_time) * video_fps)

    if start_frame > cap.get(cv2.CAP_PROP_FRAME_COUNT) or end_frame > cap.get(cv2.CAP_PROP_FRAME_COUNT):
        return jsonify({"error": "The specified time range exceeds the video length."}), 400

    frame_interval = int(video_fps / frames_per_second)
    frame_count = 0
    saved_frame_count = 0
    frame_files = []
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret or frame_count > end_frame:
            break
        if frame_count >= start_frame and frame_count % frame_interval == 0:
            frame_time = frame_count / video_fps
            frame_filename = f'{os.path.splitext(filename)[0]}_{frame_time:.2f}.png'
            frame_path = os.path.join(FRAMES_FOLDER, frame_filename)
            cv2.imwrite(frame_path, frame)
            frame_files.append(frame_filename)
            saved_frame_count += 1
        frame_count += 1

    cap.release()
    return jsonify({"frames": frame_files})

@app.route('/frames/<filename>')
def get_frame(filename):
    return send_from_directory(FRAMES_FOLDER, filename)

@app.route('/get_uploaded_images')
def get_uploaded_images():
    images = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith(('.png', '.jpg', '.jpeg', '.mp4', '.avi', '.mov'))]
    return jsonify({"images": images})

@app.route('/uploads/<path:filename>')
def uploaded_files(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/crop', methods=['POST'])
def crop_image():
    data = request.json
    filename = data['filename']
    x = int(data['x'])
    y = int(data['y'])
    width = int(data['width'])
    height = int(data['height'])
    original_width = int(data['originalWidth'])
    original_height = int(data['originalHeight'])

    filepath = os.path.join(FRAMES_FOLDER, filename)
    img = Image.open(filepath)
    
    # Ensure the crop area is within the image bounds
    x = max(0, min(x, original_width - width))
    y = max(0, min(y, original_height - height))
    
    cropped_img = img.crop((x, y, x + width, y + height))
    
    frame_size = int(request.form.get('frame_size', 128))
    cropped_img = cropped_img.resize((frame_size, frame_size), Image.LANCZOS)
    
    processed_filename = f'{os.path.splitext(filename)[0]}_x.png'
    processed_path = os.path.join(PROCESSED_FOLDER, processed_filename)
    cropped_img.save(processed_path)
    
    return jsonify({"message": "Concluído!"})

@app.route('/get_processed_images')
def get_processed_images():
    images = [f for f in os.listdir(PROCESSED_FOLDER) if f.endswith(('.png', '.jpg', '.jpeg'))]
    return jsonify({"images": images})

@app.route('/apply_segmentation', methods=['POST'])
def apply_segmentation():
    data = request.json
    image_data = data['image'].split(',')[1]
    filename = data['filename']

    # Decode base64 image
    img_data = base64.b64decode(image_data)
    img_array = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    if img is None:
        return jsonify({"message": "Failed to decode image."}), 400

    # Convert to HSV color space
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Define range for red color and create a mask
    lower_red1 = np.array([0, 70, 50])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 70, 50])
    upper_red2 = np.array([180, 255, 255])

    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = cv2.bitwise_or(mask1, mask2)

    # Create an output image with red traces in black and the rest in white
    output = cv2.bitwise_not(mask)

    # Save the segmented image
    segmented_filename = f'{os.path.splitext(filename)[0]}_segmented.png'
    segmented_path = os.path.join(SEGMENTED_FOLDER, segmented_filename)
    cv2.imwrite(segmented_path, output)
    return jsonify({"message": "Segmentation applied successfully!"})

if __name__ == '__main__':
    app.run(debug=True)