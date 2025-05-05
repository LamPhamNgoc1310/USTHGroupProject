from collections import deque
import cv2 

class CvFpsCalc():
    def __init__(self, buffer_len=1):
        self.start_tick = cv2.getTickCount()
        self.freq = 1000.0 / cv2.getTickFrequency()
        self.difftimes = deque(maxlen=buffer_len)

    def get(self):
        current_tick = cv2.getTickCount()
        different_time = (current_tick - self.start_tick) * self.freq
        self.start_tick = current_tick
        self.difftimes.append(different_time)

        Fps = 1000.0 / (sum(self.difftimes) / len(self.difftimes))
        Fps_rounded = round(Fps, 2)

        return Fps_rounded