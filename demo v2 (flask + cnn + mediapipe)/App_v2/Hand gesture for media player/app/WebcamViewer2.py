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
        # self.current_model_path = 'models/keypoint_classifier_demo_2.keras'
        self.capture = None
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5, max_num_hands=1)
        self.mp_draw = mp.solutions.drawing_utils
        self.hand_detection_enabled = False

        self.cvFpsCalc = CvFpsCalc(buffer_len=10)
        # Model-related variables
        self.models_folder = "models"  # Path to the models folder
        self.model = load_model("models/keypoint_classifier_tuning.keras")
        self.keypoint_classifier_labels = self.get_labels()
        self.last_keybind_time = time.time()

        # Shortcut mappings
        self.available_actions = [
            "Play/Pause - space",
            "Next - ctrl right",
            "Back - ctrl left",
            "Vol up - ctrl up",
            "Vol down - ctrl down",
            "Repeat - ctrl R"
        ]
        self.gesture_shortcuts = {label: self.available_actions[0] for label in self.keypoint_classifier_labels}

        # Setup UI
        self.init_ui()

        # Start Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(50)
        # self.fps_list = []

    def init_ui(self) -> None:
        # Main layout
        main_layout = QHBoxLayout()

        # Left layout (Camera and Controls)
        left_layout = QVBoxLayout()

        # Dropdown for camera selection
        self.camera_selector = QComboBox()
        cameras = self.list_cameras()
        self.camera_selector.addItems([f"Camera {i}" for i in cameras])
        self.camera_selector.currentIndexChanged.connect(self.switch_camera)
        left_layout.addWidget(self.camera_selector)

        # Dropdown for model selection
        self.model_selector = QComboBox()
        models = self.list_models()
        self.model_selector.addItems(models)
        self.model_selector.currentIndexChanged.connect(self.switch_model)
        left_layout.addWidget(self.model_selector)

        # Toggle button for hand detection
        self.toggle_button = QPushButton("Enable Hand Detection")
        self.toggle_button.clicked.connect(self.toggle_hand_detection)
        left_layout.addWidget(self.toggle_button)

        # Video Display
        self.video_label = QLabel()
        self.video_label.setFixedSize(640, 360)  # Set QLabel size to 16:9 ratio
        left_layout.addWidget(self.video_label)

        # Right layout (Gesture-Shortcut Mapping)
        right_layout = QVBoxLayout()

        # Define default shortcuts (corresponding to the image)
        default_shortcuts = {
            "0": "Play/Pause - space",
            "1": "Next - ctrl right",
            "2": "Back - ctrl left",
            "3": "Vol up - ctrl up",
            "4": "Vol down - ctrl down",
            "5": "Repeat - ctrl R",
        }

        # Add gesture labels and dropdowns
        self.dropdown_boxes = {}
        for label in self.keypoint_classifier_labels:
            row_layout = QHBoxLayout()

            # Gesture label
            gesture_label = QLabel(f"Gesture {label}")
            row_layout.addWidget(gesture_label)

            # Dropdown for shortcuts
            dropdown = QComboBox()
            dropdown.addItems(self.available_actions)
            if label in default_shortcuts:
                dropdown.setCurrentText(default_shortcuts[label])  # Set default value
            dropdown.currentTextChanged.connect(lambda action, l=label: self.update_shortcut_mapping(l, action))
            self.dropdown_boxes[label] = dropdown
            row_layout.addWidget(dropdown)

            right_layout.addLayout(row_layout)

        # Combine layouts
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)

        # Set central widget
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Initialize camera
        if cameras:
            self.switch_camera(cameras[0])


    def list_cameras(self) -> list:
        available_cameras = []
        for index in range(5):  # Check first 5 camera indices
            cap = cv2.VideoCapture(index)
            if cap.isOpened():
                available_cameras.append(index)
                cap.release()
        return available_cameras

    def list_models(self) -> list:
        models_path = "models"
        if not os.path.exists(models_path):
            return []
        return [model for model in os.listdir(models_path) if model.endswith(".keras")]

    def switch_camera(self, index: int) -> None:
        self.current_camera_index = index
        if self.capture:
            self.capture.release()
        self.capture = cv2.VideoCapture(self.current_camera_index)

    def switch_model(self, index) -> None:
        model_name = self.model_selector.currentText()
        model_path = os.path.join(self.models_folder, model_name)

        # Load the selected model
        self.model = load_model(model_path)
        self.keypoint_classifier_labels = self.get_labels()
        print(f"Loaded model: {model_name}")

    def toggle_hand_detection(self) -> None:
        self.hand_detection_enabled = not self.hand_detection_enabled
        self.toggle_button.setText("Disable Hand Detection" if self.hand_detection_enabled else "Enable Hand Detection")

    def get_labels(self) -> list:
        with open('keypoint_classifier_label_2.csv', encoding='utf-8') as file:
            keypoint_classifier_labels = csv.reader(file)
            return [row[0] for row in keypoint_classifier_labels]

    def update_shortcut_mapping(self, label, action):
        if action == "Blank":
            self.gesture_shortcuts[label] = None  # No action
        else:
            self.gesture_shortcuts[label] = action

    def keybind(self, label, last_keybind_time):
        if last_keybind_time is None:
            last_keybind_time = time.time()  # Initialize if it's None

        current_time = time.time()  # Get current time
        if current_time - last_keybind_time < 5 or label == "Unknown":  # Delay 3 seconds
            return last_keybind_time

        action = self.gesture_shortcuts.get(label)

        if action == "Play/Pause - space":
            pyautogui.hotkey('space')

        elif action == "Next - ctrl right":
            pyautogui.hotkey('ctrl', 'right')

        elif action == "Back - ctrl left":
            pyautogui.hotkey('ctrl', 'left')

        elif action == "Vol up - ctrl up":
            pyautogui.hotkey('ctrl', 'up')

        elif action == "Vol down - ctrl down":
            pyautogui.hotkey('ctrl', 'down')

        elif action == "Repeat - ctrl R":
            pyautogui.hotkey('ctrl', 'r')

        print(action)
        return current_time

    def update_frame(self) -> None:
        if not self.capture or not self.capture.isOpened():
            return

        ret, frame = self.capture.read()
        if not ret:
            return

        fps = self.cvFpsCalc.get()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.flip(frame, 1)

        # Process frame
        if self.hand_detection_enabled:
            frame.flags.writeable = False
            results = self.hands.process(frame)
            frame.flags.writeable = True

            if results.multi_hand_landmarks:
                for hand_landmarks in (results.multi_hand_landmarks):
                    self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

                    Landmark_list = calc_landmark_list(frame, hand_landmarks)

                    pre_processed_landmark_list = pre_process_landmark(Landmark_list)

                    pred = self.model.predict(np.array([pre_processed_landmark_list]), verbose=0)
                    hand_sign_id = np.argmax(pred)
                    confidence_percentage = np.ceil(pred[0][hand_sign_id] * 100)

                    # Mark as 'Unknown' if confidence is below 80%
                    if confidence_percentage < 80:
                        hand_sign_text = "Unknown"
                    else:
                        hand_sign_text = self.keypoint_classifier_labels[hand_sign_id]

                    cv2.putText(frame, f'{hand_sign_text} - {confidence_percentage}', (10, 140), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3)

                    self.last_keybind_time = self.keybind(hand_sign_text, self.last_keybind_time)  # Update the keybind time

        cv2.putText(frame, "FPS:" + str(fps), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 3, cv2.LINE_AA)

        height, width, channel = frame.shape
        step = channel * width
        q_img = QImage(frame.data, width, height, step, QImage.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(q_img).scaled(self.video_label.width(), self.video_label.height()))

    def closeEvent(self, event):
        if self.capture:
            self.capture.release()
        self.hands.close()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication([])
    viewer = WebcamViewer()
    viewer.show()
    app.exec_()
