from flask import Flask, render_template, request, session, redirect, url_for ,send_from_directory ,Response
from twilio.rest import Client
from pymongo import MongoClient
import random
import cv2
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# @app.route('/')
# def home():
#     return "Welcome to the Home Page! Go to /admin, /list, or /atten"

@app.route('/' ,methods=["GET","POST"])
def admin():
    return render_template('admin.html')

@app.route('/list')
def list():
    return render_template('list.html')

@app.route('/atten')
def atten():
    return render_template('atten.html')

# live camerA
@app.route("/cam",methods=["POST","GET"])
def cam():
    return render_template('cam.html')


@app.route('/came', methods=["GET", "POST"])
def came():
    return render_template('came.html')

# @app.route('/attendances', methods=["GET", "POST"])
# def attendances():
#     return render_template('attendances.html')

SAVE_DIR = "static/captured_images"
os.makedirs(SAVE_DIR, exist_ok=True)  # Ensure directory exists
cap = None  # Global variable to manage camera

# Generate video frames
def generate_frames():
    global cap
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Open the camera
    
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        _, buffer = cv2.imencode('.jpg', frame)  # Encode frame as JPEG
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')  # Streaming response format
    
    cap.release()

# Home page
# @app.route("/")
# def index():
#     return render_template("homepage.html")

# Capture video feed
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Open camera
@app.route('/open_camera', methods=["POST"])
def open_camera():
    return render_template("cam.html")

# Stop camera
@app.route("/stop_camera", methods=["GET", "POST"])
def stop_camera():
    global cap
    if cap is not None:
        cap.release()
        cv2.destroyAllWindows()
    return redirect("/")

# Capture Image
@app.route('/capture')
def capture():
    global cap
    if cap is None or not cap.isOpened():
        return "Camera is not open", 400
    
    success, frame = cap.read()
    if success:
        filename = f"captured_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        img_path = os.path.join(SAVE_DIR, filename)
        cv2.imwrite(img_path, frame)  # Save image
        return filename  # Return image filename
    
    return "Error capturing image", 500

# Serve captured images
@app.route('/static/<filename>')
def get_image(filename):
    return send_from_directory(SAVE_DIR, filename)


if __name__ == '__main__':
    app.run(debug=True)
