import asyncio
import websockets
import cv2
from base64 import b64encode
import numpy as np
from time import time
from pyautogui import hotkey
from tensorflow.keras.models import load_model
from threading import Thread, Lock
from mediapipe.python.solutions import hands, drawing_utils
from To_npArray import img_to_npArray
from Keybind import *
from base64 import b64encode
from Camera import *
from flask import Flask
import logging

app = Flask(__name__)
mpHands = hands
mp_drawing = drawing_utils 
hands = mpHands.Hands()

model = load_model('model2.18.0.keras')
labels = ['A', 'B', 'F', 'L', 'W', 'Y']
pred_output = ''
cLevel = 0

#Load shortcut Database
shortcutFile = 'shortcuts.txt'
shortcutDict =  loadShortcut(shortcutFile)

# loadShortcut(shortcutFile)

# Setup logging for better debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Lock for managing thread-safe operations
pred_lock = Lock()

# Function to perform prediction 
def pred(img, labels: list, model, unknownThresh=0.97):
    global pred_output, cLevel
    
    # Perform prediction in a thread-safe manner
    with pred_lock:
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

# WebSocket Server to send frames
async def send_video(websocket):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        logger.error("Error: Unable to open the camera.")
        return

    # wCam, hCam = 640, 480
    # cap.set(3, wCam)
    # cap.set(4, hCam)

    # detector = htm.handDetector(maxHands=1)

    pred_thread = None
    key_thread = None
    unknownThresh = 0.97
    prev_pred_output = ''
    count = 0
    pTime = 0
    activationTime = 10
    frame_skip = 5  # Process every 5th frame

    while True:
        success, img = cap.read()
        if not success:
            logger.error("Failed to capture frame")
            break

        output, input_IMG = img_to_npArray(img, draw=True, mpHands=mpHands, mp_drawing=mp_drawing)

        # Process frames every frame_skip intervals
        if count % frame_skip == 0:
            if (pred_thread is None) or (not pred_thread.is_alive()):
                # Start a new prediction thread
                pred_thread = Thread(target=pred, args=(input_IMG, labels, model,))
                pred_thread.start()

        if prev_pred_output == pred_output:
            count += 1
            if count >= activationTime:
                cv2.putText(output, 'ACTIVATED', (10, 200), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)
                if (key_thread is None) or (not key_thread.is_alive()):
                    # Start a new keybinding activation thread
                    key_thread = Thread(target=activateShortcut, args=(pred_output, count, activationTime, shortcutDict))
                    key_thread.start()
        else:
            count = 0
        prev_pred_output = pred_output

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(output, 'fps: ' + str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3)
        cv2.putText(output, f'{pred_output} - {cLevel}', (10, 140), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3)

        # Encode the frame to JPEG
        # _, buffer = cv2.imencode('.jpg', output)
        # frame_base64 = b64encode(buffer).decode('utf-8')

        cv2.imshow('Img', output)

        
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break
        
        # Send frame only if it's time for this frame to be processed
        if count % frame_skip == 0:
            _, buffer = cv2.imencode('.jpg', output)
            frame_base64 = b64encode(buffer).decode('utf-8')

            try:
                await websocket.send(frame_base64)
            except websockets.exceptions.ConnectionClosed:
                logger.error("WebSocket connection closed unexpectedly")
                break

    cap.release()
    cv2.destroyAllWindows()

async def start_websocket_server():
    server = await websockets.serve(send_video, "localhost", 8765)
    await server.wait_closed()

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
            
    flask_thread = Thread(target=runFlask)
    flask_thread.daemon = True
    flask_thread.start()

    # Start the WebSocket server
    asyncio.get_event_loop().run_until_complete(start_websocket_server())


if __name__ == '__main__':
    main()