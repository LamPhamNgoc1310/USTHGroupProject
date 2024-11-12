import numpy as np
import cv2
from time import time
from pyautogui import hotkey
from tensorflow.keras.models import load_model
from threading import Thread
# import mediapipe as mp
from mediapipe.python.solutions import hands, drawing_utils
from pygrabber.dshow_graph import FilterGraph


mpHands = hands
mp_drawing = drawing_utils 
hands = mpHands.Hands()

model = load_model('best3.keras')
labels = ['A', 'B', 'F', 'L', 'W', 'Y']
pred_output = ''
cLevel = 0

def img_to_npArray(img, draw: bool, mpHands, mp_drawing):
    (wristX, wristY, wristZ,
        thumb_CmcX, thumb_CmcY, thumb_CmcZ,
        thumb_McpX, thumb_McpY, thumb_McpZ,
        thumb_IpX, thumb_IpY, thumb_IpZ,
        thumb_TipX, thumb_TipY, thumb_TipZ,
        index_McpX, index_McpY, index_McpZ,
        index_PipX, index_PipY, index_PipZ,
        index_DipX, index_DipY, index_DipZ,
        index_TipX, index_TipY, index_TipZ,
        middle_McpX, middle_McpY, middle_McpZ,
        middle_PipX, middle_PipY, middle_PipZ,
        middle_DipX, middle_DipY, middle_DipZ,
        middle_TipX, middle_TipY, middle_TipZ,
        ring_McpX, ring_McpY, ring_McpZ,
        ring_PipX, ring_PipY, ring_PipZ,
        ring_DipX, ring_DipY, ring_DipZ,
        ring_TipX, ring_TipY, ring_TipZ,
        pinky_McpX, pinky_McpY, pinky_McpZ,
        pinky_PipX, pinky_PipY, pinky_PipZ,
        pinky_DipX, pinky_DipY, pinky_DipZ,
        pinky_TipX, pinky_TipY, pinky_TipZ,
        output) = extract_feature_vid(img, draw, mpHands, mp_drawing)
    
    return output, np.array([[[wristX], [wristY], [wristZ],
                                [thumb_CmcX], [thumb_CmcY], [thumb_CmcZ],
                                [thumb_McpX], [thumb_McpY], [thumb_McpZ],
                                [thumb_IpX], [thumb_IpY], [thumb_IpZ],
                                [thumb_TipX], [thumb_TipY], [thumb_TipZ],
                                [index_McpX], [index_McpY], [index_McpZ],
                                [index_PipX], [index_PipY], [index_PipZ],
                                [index_DipX], [index_DipY], [index_DipZ],
                                [index_TipX], [index_TipY], [index_TipZ],
                                [middle_McpX], [middle_McpY], [middle_McpZ],
                                [middle_PipX], [middle_PipY], [middle_PipZ],
                                [middle_DipX], [middle_DipY], [middle_DipZ],
                                [middle_TipX], [middle_TipY], [middle_TipZ],
                                [ring_McpX], [ring_McpY], [ring_McpZ],
                                [ring_PipX], [ring_PipY], [ring_PipZ],
                                [ring_DipX], [ring_DipY], [ring_DipZ],
                                [ring_TipX], [ring_TipY], [ring_TipZ],
                                [pinky_McpX], [pinky_McpY], [pinky_McpZ],
                                [pinky_PipX], [pinky_PipY], [pinky_PipZ],
                                [pinky_DipX], [pinky_DipY], [pinky_DipZ],
                                [pinky_TipX], [pinky_TipY], [pinky_TipZ]]])

# Function to Extract Feature from images or Frame
def extract_feature_vid(input_image, draw: bool, mpHands, mp_drawing):
    image = input_image
    with mpHands.Hands(static_image_mode=True, max_num_hands=1, min_detection_confidence=0.1) as hands:
        while True:
            results = hands.process(cv2.flip(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), 1))
            image_height, image_width, _ = image.shape
            # Print handedness (left v.s. right hand).
            # Caution : Uncomment these print command will resulting long log of mediapipe log
            #print(f'Handedness of {input_image}:')
            #print(results.multi_handedness)

            # Draw hand landmarks of each hand.
            # Caution : Uncomment these print command will resulting long log of mediapipe log
            #print(f'Hand landmarks of {input_image}:')
            if not results.multi_hand_landmarks:
                # Here we will set whole landmarks into zero as no handpose detected
                # in a picture wanted to extract.
                
                # Wrist Hand
                wristX = 0
                wristY = 0
                wristZ = 0
                
                # Thumb Finger
                thumb_CmcX = 0
                thumb_CmcY = 0
                thumb_CmcZ = 0
                
                thumb_McpX = 0
                thumb_McpY = 0
                thumb_McpZ = 0
                
                thumb_IpX = 0
                thumb_IpY = 0
                thumb_IpZ = 0
                
                thumb_TipX = 0
                thumb_TipY = 0
                thumb_TipZ = 0

                # Index Finger
                index_McpX = 0
                index_McpY = 0
                index_McpZ = 0
                
                index_PipX = 0
                index_PipY = 0
                index_PipZ = 0
                
                index_DipX = 0
                index_DipY = 0
                index_DipZ = 0
                
                index_TipX = 0
                index_TipY = 0
                index_TipZ = 0

                # Middle Finger
                middle_McpX = 0
                middle_McpY = 0
                middle_McpZ = 0
                
                middle_PipX = 0
                middle_PipY = 0
                middle_PipZ = 0
                
                middle_DipX = 0
                middle_DipY = 0
                middle_DipZ = 0
                
                middle_TipX = 0
                middle_TipY = 0
                middle_TipZ = 0

                # Ring Finger
                ring_McpX = 0
                ring_McpY = 0
                ring_McpZ = 0
                
                ring_PipX = 0
                ring_PipY = 0
                ring_PipZ = 0
                
                ring_DipX = 0
                ring_DipY = 0
                ring_DipZ = 0
                
                ring_TipX = 0
                ring_TipY = 0
                ring_TipZ = 0

                # Pinky Finger
                pinky_McpX = 0
                pinky_McpY = 0
                pinky_McpZ = 0
                
                pinky_PipX = 0
                pinky_PipY = 0
                pinky_PipZ = 0
                
                pinky_DipX = 0
                pinky_DipY = 0
                pinky_DipZ = 0
                
                pinky_TipX = 0
                pinky_TipY = 0
                pinky_TipZ = 0
                
                # Set image to Zero
                annotated_image = cv2.flip(input_image,1)

                # Return Whole Landmark and Image
                return (wristX, wristY, wristZ,
                        thumb_CmcX, thumb_CmcY, thumb_CmcZ,
                        thumb_McpX, thumb_McpY, thumb_McpZ,
                        thumb_IpX, thumb_IpY, thumb_IpZ,
                        thumb_TipX, thumb_TipY, thumb_TipZ,
                        index_McpX, index_McpY, index_McpZ,
                        index_PipX, index_PipY, index_PipZ,
                        index_DipX, index_DipY, index_DipZ,
                        index_TipX, index_TipY, index_TipZ,
                        middle_McpX, middle_McpY, middle_McpZ,
                        middle_PipX, middle_PipY, middle_PipZ,
                        middle_DipX, middle_DipY, middle_DipZ,
                        middle_TipX, middle_TipY, middle_TipZ,
                        ring_McpX, ring_McpY, ring_McpZ,
                        ring_PipX, ring_PipY, ring_PipZ,
                        ring_DipX, ring_DipY, ring_DipZ,
                        ring_TipX, ring_TipY, ring_TipZ,
                        pinky_McpX, pinky_McpY, pinky_McpZ,
                        pinky_PipX, pinky_PipY, pinky_PipZ,
                        pinky_DipX, pinky_DipY, pinky_DipZ,
                        pinky_TipX, pinky_TipY, pinky_TipZ,
                        annotated_image)
            
            annotated_image = cv2.flip(image.copy(), 1)
            for hand_landmarks in results.multi_hand_landmarks:
                # Wrist Hand /  Pergelangan Tangan
                wristX = hand_landmarks.landmark[mpHands.HandLandmark.WRIST].x * image_width
                wristY = hand_landmarks.landmark[mpHands.HandLandmark.WRIST].y * image_height
                wristZ = hand_landmarks.landmark[mpHands.HandLandmark.WRIST].z

                # Thumb Finger / Ibu Jari
                thumb_CmcX = hand_landmarks.landmark[mpHands.HandLandmark.THUMB_CMC].x * image_width
                thumb_CmcY = hand_landmarks.landmark[mpHands.HandLandmark.THUMB_CMC].y * image_height
                thumb_CmcZ = hand_landmarks.landmark[mpHands.HandLandmark.THUMB_CMC].z
                
                thumb_McpX = hand_landmarks.landmark[mpHands.HandLandmark.THUMB_MCP].x * image_width
                thumb_McpY = hand_landmarks.landmark[mpHands.HandLandmark.THUMB_MCP].y * image_height
                thumb_McpZ = hand_landmarks.landmark[mpHands.HandLandmark.THUMB_MCP].z
                
                thumb_IpX = hand_landmarks.landmark[mpHands.HandLandmark.THUMB_IP].x * image_width
                thumb_IpY = hand_landmarks.landmark[mpHands.HandLandmark.THUMB_IP].y * image_height
                thumb_IpZ = hand_landmarks.landmark[mpHands.HandLandmark.THUMB_IP].z
                
                thumb_TipX = hand_landmarks.landmark[mpHands.HandLandmark.THUMB_TIP].x * image_width
                thumb_TipY = hand_landmarks.landmark[mpHands.HandLandmark.THUMB_TIP].y * image_height
                thumb_TipZ = hand_landmarks.landmark[mpHands.HandLandmark.THUMB_TIP].z

                # Index Finger / Jari Telunjuk
                index_McpX = hand_landmarks.landmark[mpHands.HandLandmark.INDEX_FINGER_MCP].x * image_width
                index_McpY = hand_landmarks.landmark[mpHands.HandLandmark.INDEX_FINGER_MCP].y * image_height
                index_McpZ = hand_landmarks.landmark[mpHands.HandLandmark.INDEX_FINGER_MCP].z
                
                index_PipX = hand_landmarks.landmark[mpHands.HandLandmark.INDEX_FINGER_PIP].x * image_width
                index_PipY = hand_landmarks.landmark[mpHands.HandLandmark.INDEX_FINGER_PIP].y * image_height
                index_PipZ = hand_landmarks.landmark[mpHands.HandLandmark.INDEX_FINGER_PIP].z
                
                index_DipX = hand_landmarks.landmark[mpHands.HandLandmark.INDEX_FINGER_DIP].x * image_width
                index_DipY = hand_landmarks.landmark[mpHands.HandLandmark.INDEX_FINGER_DIP].y * image_height
                index_DipZ = hand_landmarks.landmark[mpHands.HandLandmark.INDEX_FINGER_DIP].z
                
                index_TipX = hand_landmarks.landmark[mpHands.HandLandmark.INDEX_FINGER_TIP].x * image_width
                index_TipY = hand_landmarks.landmark[mpHands.HandLandmark.INDEX_FINGER_TIP].y * image_height
                index_TipZ = hand_landmarks.landmark[mpHands.HandLandmark.INDEX_FINGER_TIP].z

                # Middle Finger / Jari Tengah
                middle_McpX = hand_landmarks.landmark[mpHands.HandLandmark.MIDDLE_FINGER_MCP].x * image_width
                middle_McpY = hand_landmarks.landmark[mpHands.HandLandmark.MIDDLE_FINGER_MCP].y * image_height
                middle_McpZ = hand_landmarks.landmark[mpHands.HandLandmark.MIDDLE_FINGER_MCP].z
                
                middle_PipX = hand_landmarks.landmark[mpHands.HandLandmark.MIDDLE_FINGER_PIP].x * image_width
                middle_PipY = hand_landmarks.landmark[mpHands.HandLandmark.MIDDLE_FINGER_PIP].y * image_height
                middle_PipZ = hand_landmarks.landmark[mpHands.HandLandmark.MIDDLE_FINGER_PIP].z
                
                middle_DipX = hand_landmarks.landmark[mpHands.HandLandmark.MIDDLE_FINGER_DIP].x * image_width
                middle_DipY = hand_landmarks.landmark[mpHands.HandLandmark.MIDDLE_FINGER_DIP].y * image_height
                middle_DipZ = hand_landmarks.landmark[mpHands.HandLandmark.MIDDLE_FINGER_DIP].z
                
                middle_TipX = hand_landmarks.landmark[mpHands.HandLandmark.MIDDLE_FINGER_TIP].x * image_width
                middle_TipY = hand_landmarks.landmark[mpHands.HandLandmark.MIDDLE_FINGER_TIP].y * image_height
                middle_TipZ = hand_landmarks.landmark[mpHands.HandLandmark.MIDDLE_FINGER_TIP].z

                # Ring Finger / Jari Cincin
                ring_McpX = hand_landmarks.landmark[mpHands.HandLandmark.RING_FINGER_MCP].x * image_width
                ring_McpY = hand_landmarks.landmark[mpHands.HandLandmark.RING_FINGER_MCP].y * image_height
                ring_McpZ = hand_landmarks.landmark[mpHands.HandLandmark.RING_FINGER_MCP].z
                
                ring_PipX = hand_landmarks.landmark[mpHands.HandLandmark.RING_FINGER_PIP].x * image_width
                ring_PipY = hand_landmarks.landmark[mpHands.HandLandmark.RING_FINGER_PIP].y * image_height
                ring_PipZ = hand_landmarks.landmark[mpHands.HandLandmark.RING_FINGER_PIP].z
                
                ring_DipX = hand_landmarks.landmark[mpHands.HandLandmark.RING_FINGER_DIP].x * image_width
                ring_DipY = hand_landmarks.landmark[mpHands.HandLandmark.RING_FINGER_DIP].y * image_height
                ring_DipZ = hand_landmarks.landmark[mpHands.HandLandmark.RING_FINGER_DIP].z
                
                ring_TipX = hand_landmarks.landmark[mpHands.HandLandmark.RING_FINGER_TIP].x * image_width
                ring_TipY = hand_landmarks.landmark[mpHands.HandLandmark.RING_FINGER_TIP].y * image_height
                ring_TipZ = hand_landmarks.landmark[mpHands.HandLandmark.RING_FINGER_TIP].z

                # Pinky Finger / Jari Kelingking
                pinky_McpX = hand_landmarks.landmark[mpHands.HandLandmark.PINKY_MCP].x * image_width
                pinky_McpY = hand_landmarks.landmark[mpHands.HandLandmark.PINKY_MCP].y * image_height
                pinky_McpZ = hand_landmarks.landmark[mpHands.HandLandmark.PINKY_MCP].z
                
                pinky_PipX = hand_landmarks.landmark[mpHands.HandLandmark.PINKY_PIP].x * image_width
                pinky_PipY = hand_landmarks.landmark[mpHands.HandLandmark.PINKY_PIP].y * image_height
                pinky_PipZ = hand_landmarks.landmark[mpHands.HandLandmark.PINKY_PIP].z
                
                pinky_DipX = hand_landmarks.landmark[mpHands.HandLandmark.PINKY_DIP].x * image_width
                pinky_DipY = hand_landmarks.landmark[mpHands.HandLandmark.PINKY_DIP].y * image_height
                pinky_DipZ = hand_landmarks.landmark[mpHands.HandLandmark.PINKY_DIP].z
                
                pinky_TipX = hand_landmarks.landmark[mpHands.HandLandmark.PINKY_TIP].x * image_width
                pinky_TipY = hand_landmarks.landmark[mpHands.HandLandmark.PINKY_TIP].y * image_height
                pinky_TipZ = hand_landmarks.landmark[mpHands.HandLandmark.PINKY_TIP].z

                # Draw the Skeleton
                if draw:
                    mp_drawing.draw_landmarks(annotated_image, hand_landmarks, mpHands.HAND_CONNECTIONS)
                
            return (wristX, wristY, wristZ,
                    thumb_CmcX, thumb_CmcY, thumb_CmcZ,
                    thumb_McpX, thumb_McpY, thumb_McpZ,
                    thumb_IpX, thumb_IpY, thumb_IpZ,
                    thumb_TipX, thumb_TipY, thumb_TipZ,
                    index_McpX, index_McpY, index_McpZ,
                    index_PipX, index_PipY, index_PipZ,
                    index_DipX, index_DipY, index_DipZ,
                    index_TipX, index_TipY, index_TipZ,
                    middle_McpX, middle_McpY, middle_McpZ,
                    middle_PipX, middle_PipY, middle_PipZ,
                    middle_DipX, middle_DipY, middle_DipZ,
                    middle_TipX, middle_TipY, middle_TipZ,
                    ring_McpX, ring_McpY, ring_McpZ,
                    ring_PipX, ring_PipY, ring_PipZ,
                    ring_DipX, ring_DipY, ring_DipZ,
                    ring_TipX, ring_TipY, ring_TipZ,
                    pinky_McpX, pinky_McpY, pinky_McpZ,
                    pinky_PipX, pinky_PipY, pinky_PipZ,
                    pinky_DipX, pinky_DipY, pinky_DipZ,
                    pinky_TipX, pinky_TipY, pinky_TipZ,
                    annotated_image)


def pred(img, labels: list, model, unknownThresh=0.97):
    global pred_output, cLevel
    
    pred = model.predict(img, verbose=0)
    max_position = np.argmax(pred)
    pred_output = labels[max_position]
    if pred[0][max_position] < unknownThresh: 
        pred_output = 'unknown gesture'
    cLevel = np.ceil(pred[0][max_position] * 100) / 100

def activateShortcut(pred_output, count, activationTime):
    # count tăng liên tục
    # count > activation time (which is a const) -> hiện chữ "activated"
    # 
    if pred_output == 'L': hotkey('ctrl', 'up')
    if pred_output == 'W': hotkey('ctrl', 'down')
    if pred_output == 'F' and count % (activationTime/2) == 0: hotkey('ctrl', 'left') 
    # control tốc độ thôi không có gì hot
    if pred_output == 'B' and count % (activationTime/2) == 0: hotkey('ctrl', 'right')
    if count == activationTime:
        # để nó activate 1 lần chứ không liên tục cho mỗi loop
        if pred_output == 'A': hotkey('space')
        if pred_output == 'Y': hotkey('ctrl', 'r')

def list_cameras():
    graph = FilterGraph()
    devices = graph.get_input_devices()
    return devices

def main():
    cameras = list_cameras()
    for idx, camera in enumerate(cameras):
        print(f"Camera {idx}: {camera}")
    
    while True:
        try:
            camSaus = int(input("Select Available Camera Source: "))
            if camSaus < len(cameras): break
            print("Camera not Available")
        except Exception as e: 
            print("----------")
            print("Error occurred:")
            print(e)
            print("----------")
            
    
    
    
    
    cap = cv2.VideoCapture(camSaus)
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

        cv2.putText(output, f'{pred_output} - {cLevel}', (10, 140), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3)

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
