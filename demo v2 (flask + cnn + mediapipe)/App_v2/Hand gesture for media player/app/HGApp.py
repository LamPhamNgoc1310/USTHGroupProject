import cv2
import mediapipe as mp
import pyautogui
import csv
import time
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QWidget
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer
from CvFpsCalc import CvFpsCalc
from functions import *
from tensorflow.keras.models import load_model
import os


class WebcamViewer(QMainWindow):

    def __init__(self):
        super().__init__()
        

        self.setWindowTitle("Webcam Viewer with Hand Detection")
        self.setGeometry(100, 100, 1280, 720)  # Set to 16:9 ratio with 720p resolution
        self.setFixedSize(1280, 720)  # Make the window non-resizable

        # Variables
        self.current_camera_index = 0

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5, max_num_hands=1)
        self.mp_draw = mp.solutions.drawing_utils
        self.hand_detection_enabled = False
        self.cvFpsCalc = CvFpsCalc(buffer_len=10)

        self.models_folder = "models"  # Path to the models folder
        self.model = load_model("models/keypoint_classifier_tuning.keras")
        self.keypoint_classifier_labels = self.get_labels()
        self.



        self.last_keybind_time = time.time()


        # Setup UI
        self.init_ui()

        # Start Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(50)
        # self.fps_list = []
