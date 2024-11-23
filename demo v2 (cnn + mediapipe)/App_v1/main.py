import sys
import json
import numpy as np
import cv2
from time import time
from tensorflow.keras.models import load_model
# import tensorflow as tf
# from tensorflow import keras
from threading import Thread, Lock
from mediapipe.python.solutions import hands, drawing_utils
from To_npArray import img_to_npArray
# from Keybind import *
from base64 import b64encode
from zmq import Context, PUB
from Camera import *
from flask import Flask, jsonify
import os

# Setup ZeroMQ to stream frames
context = Context()
socket = context.socket(PUB)
socket.bind("tcp://*:5555")

app = Flask(__name__)
mpHands = hands
mp_drawing = drawing_utils 
hands = mpHands.Hands()

model = load_model('model2.18.0.keras')
labels = ['A', 'B', 'F', 'L', 'W', 'Y']
pred_output = ''
cLevel = 0

# Load shortcut Database
# shortcutFile = 'shortcuts.txt'
# shortcutDict =  loadShortcut(shortcutFile)

# loadShortcut(shortcutFile)

output_lock = Lock()

# Function to perform prediction 
def pred(img, labels: list, model, unknownThresh=0.97):
    global pred_output, cLevel

    with output_lock:
        pred = model.predict(img, verbose=0)
        max_position = np.argmax(pred)
        pred_output = labels[max_position]
        if pred[0][max_position] < unknownThresh: 
            pred_output = 'unknown gesture'
        cLevel = np.ceil(pred[0][max_position] * 100) / 100

# Function to save video received from Electron
def save_video(video_data):
    try:
        # Assuming video_data is a base64-encoded video buffer (string)
        video_bytes = b64encode(video_data)

        # Define the save path (use user-specified file path from Electron)
        save_path = 'video_output.webm'  # You can adjust this according to Electron's dialog input

        with open(save_path, 'wb') as video_file:
            video_file.write(video_bytes)

        print(f"Video saved successfully at {save_path}")
        return {"success": True, "message": f"Video saved to {save_path}"}
    except Exception as e:
        print(f"Error saving video: {e}")
        return {"success": False, "message": str(e)}

# Listen for incoming commands from Electron (via stdin)
def listen_for_commands():
    while True:
        try:
            message = sys.stdin.readline().strip()  # Read incoming message from Electron
            if message:
                data = json.loads(message)  # Convert JSON string to Python dictionary

                if data["type"] == "save-video":
                    response = save_video(data["data"])
                    sys.stdout.write(json.dumps(response) + "\n")  # Send response back to Electron
                    sys.stdout.flush()
        except Exception as e:
            sys.stderr.write(f"Error: {e}\n")
            sys.stderr.flush()


@app.route('/shortcuts', methods=['GET'])
def getShortcut():
    return getShortcutAPI()

@app.route('/camera_sources', methods=['GET'])
def getCameraSource():
    return getCameraSourceAPI()

current_camera_source = 0  # Default camera source
camera_thread = None

@app.route('/set_camera/<int:camera_id>', methods=['POST'])
def set_camera(camera_id):
    global current_camera_source, camera_thread

    # Update the camera source
    current_camera_source = camera_id

    # Restart the camera thread if it's running
    if camera_thread and camera_thread.is_alive():
        camera_thread.join(timeout=1)

    # Start a new camera thread with the updated source
    camera_thread = Thread(target=start_camera_stream, args=(current_camera_source,))
    camera_thread.daemon = True
    camera_thread.start()

    return jsonify({"success": True, "message": f"Camera switched to {camera_id}"})


def start_camera_stream(camera_source):
    cap = cv2.VideoCapture(camera_source)
    if not cap.isOpened():
        print(f"Error: Unable to open camera source {camera_source}. Please check the camera connection.")
        return


    wCam, hCam = 640, 480
    cap.set(3, wCam)
    cap.set(4, hCam)

    pred_thread = None
    key_thread = None
    unknownThresh = 0.97
    prev_pred_output = ''
    count = 0
    pTime = 0
    activationTime = 10

    while True:
        success, img = cap.read()
        if not success:
            print(f"Error: Failed to grab frame from camera {camera_source}")
            break

        output, input_IMG = img_to_npArray(img, draw=True, mpHands=mpHands, mp_drawing=mp_drawing)

        # Prediction logic
        if (pred_thread is None) or (not pred_thread.is_alive()):
            # print("Starting prediction thread")
            pred_thread = Thread(target=pred, args=(input_IMG, labels, model,))
            pred_thread.start()

        if prev_pred_output == pred_output:
            count += 1
            if count >= activationTime:
                cv2.putText(output, 'ACTIVATED', (10, 200), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)
                if (key_thread is None) or (not key_thread.is_alive()):
                    # print("Starting key thread")
                    key_thread = Thread(target=activateShortcut, args=(pred_output, count, activationTime,shortcutDict))
                    key_thread.start()
        else:
            count = 0
        prev_pred_output = pred_output

        # FPS calculation
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        # Hiển thị fps
        cv2.putText(output, 'fps: ' + str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3)
        # Hiển thị pred label và confidence level
        cv2.putText(output, f'{pred_output} - {cLevel}', (10, 140), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3)
        
        # Encode the frame to Base64
        _, buffer = cv2.imencode('.jpg', output)
        frame_base64 = b64encode(buffer).decode('utf-8')

        # Compress the frame before encoding to base64 if have problem with performance/memory usage
        # encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]  # Adjust the quality as needed
        # _, buffer = cv2.imencode('.jpg', output, encode_param)
        # frame_base64 = b64encode(buffer).decode('utf-8')

        # Send the frame over ZeroMQ
        socket.send_string(frame_base64)

        # Display the frame locally
        cv2.imshow('Img', output)
        
        # cv2.waitKey(1)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # time.sleep(0.1)  # Add a short delay to reduce the frequency of thread creation

    cap.release()
    cv2.destroyAllWindows()

def runFlask():
    app.run(debug=True, use_reloader=False)

def main():
    # User will input this on the UI
    # cameras = list_cameras()
    # for idx, camera in enumerate(cameras):
    #     print(f"Camera {idx}: {camera}")
    
    # while True:
    #     try:
    #         camSaus = int(input("Select Available Camera Source: "))
    #         if camSaus < len(cameras): break
    #         print("Camera not Available")
    #     except Exception as e: 
    #         print("----------")
    #         print("Error occurred:")
    #         print(e)
    #         print("----------")
    
    # Start the Flask server
    flask_thread = Thread(target=runFlask)
    flask_thread.daemon = True
    flask_thread.start()

    # Start the command listener (e.g., saving video data)
    command_thread = Thread(target=listen_for_commands)
    command_thread.daemon = True
    command_thread.start()

    # Start the initial camera stream
    camera_thread = Thread(target=start_camera_stream, args=(current_camera_source,))
    camera_thread.daemon = True
    camera_thread.start()

    # detector = htm.handDetector(maxHands=1)

if __name__ == '__main__':
    main()