import numpy as np
import cv2
import time
# import HandTrackingModule as htm
from pyautogui import hotkey
import tensorflow as tf
from utils import *
import threading
import os
import time
import logging
 
# Suppress TensorFlow warnings
logging.getLogger('tensorflow').setLevel(logging.ERROR)




mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils 
hands = mp_hands.Hands()

model = tf.keras.models.load_model('best3.keras')
labels = ['A', 'B', 'F', 'L', 'W', 'Y']
pred_output = ''
cLevel = 0

def pred(img, labels: list, model, unknownThresh=0.97):
    global pred_output, cLevel
    
    pred = model.predict(img, verbose=0)
    max_position = np.argmax(pred)
    pred_output = labels[max_position]
    if pred[0][max_position] < unknownThresh: 
        pred_output = 'unknown gesture'
    cLevel = np.ceil(pred[0][max_position] * 100) / 100

def activateShortcut(pred_output, count, activationTime):
    if pred_output == 'L': hotkey('ctrl', 'up')
    if pred_output == 'W': hotkey('ctrl', 'down')
    if pred_output == 'F' and count % (activationTime/2) == 0: hotkey('ctrl', 'left')
    if pred_output == 'B' and count % (activationTime/2) == 0: hotkey('ctrl', 'right')
    if count == activationTime:
        if pred_output == 'A': hotkey('space')
        if pred_output == 'Y': hotkey('ctrl', 'r')

def main():
    wCam, hCam = 640, 480

    cap = cv2.VideoCapture(0)
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
        output, input_IMG = img_to_npArray(img, draw=True, mp_hands=mp_hands, mp_drawing=mp_drawing)

        if (pred_thread is None) or (not pred_thread.is_alive()):
            print("Starting prediction thread")
            pred_thread = threading.Thread(target=pred, args=(input_IMG, labels, model,))
            pred_thread.start()

        cv2.putText(output, f'{pred_output} - {cLevel}', (10, 140), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3)

        if prev_pred_output == pred_output:
            count += 1
            if count >= activationTime:
                cv2.putText(output, 'ACTIVATED', (10, 200), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)
                if (key_thread is None) or (not key_thread.is_alive()):
                    print("Starting key thread")
                    key_thread = threading.Thread(target=activateShortcut, args=(pred_output, count, activationTime,))
                    key_thread.start()
        else:
            count = 0
        prev_pred_output = pred_output

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(output, 'fps: ' + str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3)

        cv2.imshow('Img', output)
        cv2.waitKey(1)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # time.sleep(0.1)  # Add a short delay to reduce the frequency of thread creation

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
