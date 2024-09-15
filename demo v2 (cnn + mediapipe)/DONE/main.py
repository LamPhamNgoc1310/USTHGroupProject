import numpy as np
import cv2
import time
import HandTrackingModule as htm
from pyautogui import hotkey
import tensorflow as tf
from utils import *

model = tf.keras.models.load_model('best2.keras')
labels = ['A', 'B', 'F', 'L', 'W', 'Y']





def main():
    #########################################
    wCam, hCam = 640, 480
    #########################################


    cap = cv2.VideoCapture(0)

    # set WIDTH
    cap.set(3, wCam)
    # set HIGHT
    cap.set(4, hCam)

    detector = htm.handDetector(detectionCon=0.7, maxHands=1)

    unknownThresh = 0.97
    prev_pred_output = ''
    count = 0
    pTime = 0

    # i dont really know the sec or min, 
    # it's just the faster it loop, the faster to get it to activate
    activationTime = 10 


    while True:
        success, img = cap.read()
        img = detector.findHands(img, draw= False)
        lmList = detector.findPosition(img, draw=False)
        # print(results.multi_hand_landmarks)
        
        # ------------>if hand detected in cam<------------
        if len(lmList) != 0:
            output, input_IMG = img_to_npArray(img)
        
        # -----------------> prediction made here <------------
            pred = model.predict(input_IMG,verbose=0)
            max_position = np.argmax(pred)
            pred_output = labels[max_position]
            if pred[0][max_position] < unknownThresh: pred_output = 'unknown gesture'
            rounded_value = np.ceil(pred[0][max_position] * 100) / 100
            cv2.putText(output, f'{pred_output} - {rounded_value}',(10,140),cv2.FONT_HERSHEY_PLAIN, 3, (255,255,255), 3)


        # -----------------> delay activation <-----------------
            if prev_pred_output == pred_output:
                count+=1
                if count >= activationTime:
                    cv2.putText(output, f'ACTIVATED',(10,200),cv2.FONT_HERSHEY_PLAIN, 3, (0,255,0), 3)
                    if pred_output == 'L': hotkey('ctrl', 'up')
                    if pred_output == 'W': hotkey('ctrl', 'down')
                    if pred_output == 'F': hotkey('ctrl', 'left')
                    
                    # -----------------> ACTION MADE <-----------------
                    if count == activationTime:
                        if pred_output == 'A': hotkey('space')
                        if pred_output == 'B': hotkey('ctrl', 'right')
                        if pred_output == 'Y': hotkey('ctrl', 'r')
            else: count = 0
            prev_pred_output = pred_output



        # ------------> hand not in cam <---------------
        else: output = cv2.flip(img,1)
        
        
        
        # ------------>display FPS<------------
        cTime = time.time()
        fps = 1/(cTime-pTime)
        pTime = cTime
        cv2.putText(output,'fps:   ' + str(int(fps)), (10,70), cv2.FONT_HERSHEY_PLAIN, 3, (255,255,255), 3)
        
        
        
        # ------------>show vid<------------
        cv2.imshow('Img', output)
        cv2.waitKey(1)
        
        # Press (or spam) 'q' to close window
        if cv2.waitKey(1) & 0xFF == ord('q'): break

    # Release the capture and close the window
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
