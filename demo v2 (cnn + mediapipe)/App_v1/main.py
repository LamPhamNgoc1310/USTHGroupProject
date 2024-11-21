import numpy as np
import cv2
from time import time
from pyautogui import hotkey
from tensorflow.keras.models import load_model
from threading import Thread
from mediapipe.python.solutions import hands, drawing_utils
from pygrabber.dshow_graph import FilterGraph
from To_npArray import img_to_npArray
from Keybind import activateShortcut
from base64 import b64encode
from zmq import Context, PUB

# Setup ZeroMQ to stream frames
context = Context()
socket = context.socket(PUB)
socket.bind("tcp://*:5555")

mpHands = hands
mp_drawing = drawing_utils 
hands = mpHands.Hands()

model = load_model('model2.18.0.keras')
labels = ['A', 'B', 'F', 'L', 'W', 'Y']
pred_output = ''
cLevel = 0

#Shortcut Database
shortcutFile = 'shortcuts.txt'
shortcutDict =  loadShortcut(shortcutFile)

# Function to perform prediction 
def pred(img, labels: list, model, unknownThresh=0.97):
    global pred_output, cLevel
    
    pred = model.predict(img, verbose=0)
    max_position = np.argmax(pred)
    pred_output = labels[max_position]
    if pred[0][max_position] < unknownThresh: 
        pred_output = 'unknown gesture'
    cLevel = np.ceil(pred[0][max_position] * 100) / 100
    

# Function to list all the available camera sources
# def list_cameras():
#     graph = FilterGraph()
#     devices = graph.get_input_devices()
#     return devices

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
            
    
    
    
    
    cap = cv2.VideoCapture(0)
    if cap is None or not cap.isOpened():
        print ('Warning: unable to open video source ')
        return
    
    
    
    wCam, hCam = 640, 480
    cap.set(3, wCam)
    cap.set(4, hCam)

    # detector = htm.handDetector(maxHands=1)
    
    pred_thread = None
    key_thread = None
    unknownThresh = 0.97
    prev_pred_output = ''
    count = 0
    pTime = 0
    activationTime = 10


    while True:
        success, img = cap.read()
        output, input_IMG = img_to_npArray(img, draw=True, mpHands=mpHands, mp_drawing=mp_drawing)

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
                    key_thread = Thread(target=activateShortcut, args=(pred_output, count, activationTime,))
                    key_thread.start()
        else:
            count = 0
        prev_pred_output = pred_output

        cTime = time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        # hiển thị fps
        cv2.putText(output, 'fps: ' + str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3)
        # hiển thị pred label và confidence level
        cv2.putText(output, f'{pred_output} - {cLevel}', (10, 140), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3)
        
        # Encode the frame to Base64
        _, buffer = cv2.imencode('.jpg', output)
        frame_base64 = b64encode(buffer).decode('utf-8')
    
        # Send the frame
        socket.send_string(frame_base64)
        
        
        cv2.imshow('Img', output)
        # cv2.waitKey(1)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # time.sleep(0.1)  # Add a short delay to reduce the frequency of thread creation

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
