from flask import Flask, render_template, redirect, url_for, request, Response, jsonify
import os
import cv2
import numpy as np
from main import ObjectTracker
from ultralytics import YOLO
import json
# import torch


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'  # Define your upload folder

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Variable to store play/pause state
play_video = False
cancel_stream = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/detect_screen')
def detect_screen():
    return render_template('detect_screen.html')

@app.route('/upload_video', methods=['POST'])
def upload_video():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return jsonify({'filename': filename}), 200

def generate_video_stream(filename):
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    is_mask = True
    cap = cv2.VideoCapture(video_path)


    # Load YOLO model
    model = YOLO("model/vehicle_plat.pt")
    class_list = model.model.names
    # print(class_list)

    # Read ROI points from JSON
    with open("data.json") as f:
        data = json.load(f)

    roi = data["boxes"][0]["points"]
    roi = np.array(roi, dtype=np.int32)
    roi = roi.reshape((1, -1, 2))

    # Normalize the ROI points to the original frame size
    frame_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    frame_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    roi_normalized = roi.astype(np.float32)
    roi_normalized[:, :, 0] /= float(data["boxes"][0]["width"])
    roi_normalized[:, :, 1] /= float(data["boxes"][0]["height"])

    # Rescale the ROI points to the new frame size
    roi_rescaled = roi_normalized.copy()
    roi_rescaled[:, :, 0] *= frame_width
    roi_rescaled[:, :, 1] *= frame_height

    # Convert back to int32 type
    roi_rescaled = roi_rescaled.astype(np.int32)

    # Initialize frame index
    i = 0
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    # Initialize ObjectTracker
    tracker = ObjectTracker(max_distance_threshold=50)
    data = {
    "total_vehicle": 0,
    "total_license": 0,
    "current_vehicle": 0,
    "current_license": 0
    }
    while cap.isOpened():
        global play_video
        if not play_video:
            continue
        
        ret, frame = cap.read()
        if not ret or not cancel_stream:
            break

        # Apply mask to the frame if is_mask is True
        if is_mask:
            mask = np.zeros_like(frame)
            cv2.fillPoly(mask, [roi_rescaled], (255, 255, 255))
            mask_frame = cv2.bitwise_and(frame, mask)
        else:
            mask_frame = frame

        # Get predictions from the model
        results = model(mask_frame, iou=0.40, conf=0.35, show=False)

        boxes = results[0].boxes.xyxy.cpu().numpy()
        cls = results[0].boxes.cls.cpu().numpy().tolist()
        # print(cls)
        # break

        # Update ObjectTracker with detections
        detections = []
        numberplate_detections = []
        
        for box, label in zip(boxes, cls):
            x1, y1, x2, y2 = int(box[0]), int(box[1]), int(box[2]), int(box[3])
            
            # print(type(label))
            # print(str(int(label)))
            label_name = class_list[int(label)]
            # print(label_name)
            
            if label_name == "number plate":
                numberplate_detections.append({'bbox': (x1, y1, x2, y2)})
            else:
                detections.append({'bbox': (x1, y1, x2, y2)})
        
        # print(f"number_plate: {numberplate_detections}")
        # print(f"detections: {detections}")
        
        # Update tracks with detections
        tracker.update_tracks(detections)
        tracker.assign_numberplates(numberplate_detections)
        
        # Draw ROI on the frame
        cv2.polylines(frame, [roi_rescaled], True, (0, 170, 165), 3)

        # Draw tracked objects on the frame with IDs
        
        # for track in tracker.tracks:
        #     if track.object_class =="vehicle":
        #         print(f"track_id:{track.object_id} - track")
                
        for track in tracker.tracks:
            color = (255, 0, 0) if track.object_class == "vehicle" else (0, 255, 0)
            x1, y1, x2, y2 = track.bbox
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
            # x1, y1, x2, y2 = int(track.center[0] - 50), int(track.center[1] - 50), int(track.center[0] + 50), int(track.center[1] + 50)
            cv2.putText(frame, f"{track.object_id}- {track.object_class}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 3)
            
            # #plot number plate
            # if track.numberplate_bbox!= None:
            #     x1,y1,x2,y2 = track.numberplate_bbox
            #     cv2.rectangle(frame, (x1, y1), (x2, y2), (255,0,0), 3)
        
        for numberplate in numberplate_detections:
            x1, y1, x2, y2 =numberplate["bbox"]
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 3)
        
        data["total_vehicle"] = tracker.next_object_id - 1
        data["total_license"] = len(numberplate_detections)
        data["current_vehicle"] = len(detections)
        data["current_license"] = len(numberplate_detections)

        with open("static/assets/json/track.json", "w") as f:
            f.write(json.dumps(data))
    
        
        
        cv2.putText(frame, f"unique vehicle count:-{tracker.next_object_id -1}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 3)        
        
        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
    cap.release()

@app.route('/detect_video/<filename>')
def video_feed(filename):
    return Response(generate_video_stream(filename), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/play_pause', methods=['POST'])
def play_pause():
    global play_video
    
    play_video = not play_video
    return jsonify({'playing': play_video})


@app.route('/track_data')
def track_data():
    with open("track.json") as f:
        data = json.load(f)
    return jsonify(data)


@app.route('/cancel_stream', methods=['POST'])
def cancel_stream():
    global play_video
    global cancel_stream
    cancel_stream = True
    play_video = False
    return jsonify({'status': 'Stream canceled'})

if __name__ == '__main__':
    app.run(debug=True)
