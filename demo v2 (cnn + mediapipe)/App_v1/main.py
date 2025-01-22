import cv2
import numpy as np
from time import time
from tensorflow.keras.models import load_model
from threading import Thread, Lock
from mediapipe.python.solutions import hands, drawing_utils
from FrameUpdate import *
from Keybind import *
from Camera import *
from flask import Flask, Response, jsonify
from flask_cors import CORS
import logging

app = Flask(__name__)
CORS(app)
mpHands = hands
mp_drawing = drawing_utils 
hands = mpHands.Hands()
is_shutting_down = False


model = load_model('keypoint_classifier.keras')
labels = ['0' ,'1', '2', '3', '4', '5']
pred_output = ''
cLevel = 0

#Load shortcut Database
shortcutFile = 'shortcuts.txt'
shortcutDict =  loadShortcut(shortcutFile)

loadShortcut(shortcutFile)

# Setup logging for better debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Lock for managing thread-safe operations
pred_lock = Lock()

# Function to perform prediction 
def pred(img, labels: list, model, unknownThresh=0.97):
    global pred_output, cLevel, is_shutting_down
    
    # Perform prediction in a thread-safe manner
    with pred_lock:
        if is_shutting_down:
            return  # Exit early if the server is shutting down
            
        pred = model.predict(img, verbose=0)
        max_position = np.argmax(pred)
        pred_output = labels[max_position]
        if pred[0][max_position] < unknownThresh:
            pred_output = 'unknown gesture'
        cLevel = np.ceil(pred[0][max_position] * 100) / 100
    

@app.route('/shortcuts', methods=['GET'])
def getShortcut():
    return getShortcutAPI()

@app.route('/camera_sources', methods=['GET'])
def getCameraSource():
    return getCameraSourceAPI()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "running"}), 200

# Flask route to stream video
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

cap_lock = Lock()
def generate_frames():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        logger.error("Error: Unable to open the camera.")
        return

    target_fps = 11  # Desired frames per second
    frame_duration = 1.0 / target_fps  # Duration of each frame in seconds
    pred_thread = None
    key_thread = None
    unknownThresh = 0.97
    prev_pred_output = ''
    count = 0
    pTime = 0
    activationTime = 10

    wCam, hCam = 640, 480
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, wCam)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, hCam)

    # detector = htm.handDetector(maxHands=1)

    
    while True:
        cTime = time.time()
        
        with cap_lock:  # Ensure single-threaded access to the camera
            success, img = cap.read()
            if not success:
                logger.error(f"Failed to capture frame at time {cTime}")
                break
        
        img = cv2.resize(img, (wCam, hCam))

        output, input_IMG = img_to_npArray(img, draw=True, mpHands=mpHands, mp_drawing=mp_drawing)

        if (pred_thread is None) or (not pred_thread.is_alive()):
            # Start a new prediction thread
            pred_thread = Thread(target=pred, args=(input_IMG, labels, model,unknownThresh))
            pred_thread.start()

        count += 1
        if prev_pred_output != pred_output: 
            count = 0

        if count >= activationTime and pred_output != "unknown gesture":
            cv2.putText(output, 'ACTIVATED', (10, 200), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)
            activateShortcut(pred_output, count, activationTime,shortcutDict)
            if (key_thread is None) or (not key_thread.is_alive()):
                    # Start a new keybinding activation thread
                    key_thread = Thread(target=activateShortcut, args=(pred_output, count, activationTime, shortcutDict))
                    key_thread.start()

        prev_pred_output = pred_output

        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(output, 'fps: ' + str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3)
        cv2.putText(output, f'{pred_output} - {cLevel}', (10, 140), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3)

        # cv2.imshow('Img', output)

        # Calculate the time taken to process the frame
        elapsed_time = time.time() - cTime
        remaining_time = frame_duration - elapsed_time

        # Introduce a delay to maintain the target FPS
        if remaining_time > 0:
            time.sleep(remaining_time)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        _, buffer = cv2.imencode('.jpg', output)
        frame = buffer.tobytes()
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()
    cv2.destroyAllWindows()



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
            
    return 0

def run_flask():
    app.run(debug=False, use_reloader=False)

if __name__ == '__main__':
    flask_thread = Thread(target=run_flask)
    flask_thread.start()