import cv2
from cv2.typing import MatLike
import time
import mediapipe as mp

class handDetector():
    def __init__(self, 
                 mode= False, 
                 maxHands= 2, 
                 model_complexity=1,
                 detectionCon= 0.5, 
                 trackCon= 0.5):

        self.mode = mode
        self.maxHands = maxHands
        self.model_complexity = model_complexity
        self.detectionCon = detectionCon
        self.trackCon = trackCon


        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, 
                                        self.maxHands, 
                                        self.model_complexity,
                                        self.detectionCon, 
                                        self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils


    def findHands(self, img: MatLike, draw= True) -> MatLike:
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        
        # print(results.multi_hand_landmarks)
        if draw:
            if self.results.multi_hand_landmarks:
                for handLms in self.results.multi_hand_landmarks:
                        # NOTE: vẽ các landmarks và nối chúng
                        self.mpDraw.draw_landmarks(img, 
                                                   handLms, 
                                                   self.mpHands.HAND_CONNECTIONS)
        return img


    def findPosition(self, img: MatLike, handNo= 0, draw= True) -> list:
        lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            
            
            for id, lm in enumerate(myHand.landmark):
                # print(id,lm)
                
                h, w, c = img.shape
                cx, cy = int(lm.x*w), int(lm.y*h)
                # print(id, cx, cy)
                lmList.append([id, cx, cy])
                
                if draw:
                    cv2.circle(img, (cx,cy), 7, (255,0,255), cv2.FILLED)
        
        return lmList


def main():

    pTime = 0
    cTime = 0
    cap = cv2.VideoCapture(0)
    detector = handDetector()

    lmNo = 0

    while True:
        success, img = cap.read()
        img = detector.findHands(img, draw= True)
        lmList = detector.findPosition(img, draw= False)

        # NOTE: lấy toạ độ của 1 landmark
        if len(lmList) != 0:
            print(lmList[lmNo])
            cx,cy = lmList[lmNo][1], lmList[lmNo][2]
            cv2.circle(img, (cx,cy), 7, (255,0,255), cv2.FILLED)

        cTime = time.time()
        fps = 1/(cTime-pTime)
        pTime = cTime
        
        cv2.putText(img,'fps:   ' + str(int(fps)), (10,70), cv2.FONT_HERSHEY_PLAIN, 3, (255,255,255), 3)
        
        
        cv2.imshow('Img', img)
        cv2.waitKey(1)




if __name__ == '__main__':
    main()