import signal
import threading
from flask import Flask, Response, jsonify
from flask_cors import CORS
import cv2 as cv2
import numpy as np
from tensorflow.keras.models import load_model
import mediapipe as mp
from Keybind import *
from Camera import *
from functions import *
from CvFpsCalc import CvFpsCalc
import logging
import copy
import time


app = Flask(__name__)
CORS(app)


# Setup logging for better debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# Global Variables
shutdown_event = threading.Event()  # Event to signal shutdown
cap_lock = threading.Lock()
last_keybind_time = time.time()  # Initialize the keybind time


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




def generate_frames():
    global last_keybind_time  # Access the global variable for last keybind time
    
    
    
    """Argument Parsing"""
    args = get_args()

    cap_device = args.device
    cap_width = args.width
    cap_height = args.height   

    use_static_image_mode = args.use_static_image_mode
    min_detection_confidence = args.min_detection_confidence
    min_tracking_confidence = args.min_tracking_confidence  

    print(use_static_image_mode, min_detection_confidence, min_tracking_confidence)

    use_brect = True
    prediction_enabled = True

    # Initialize last_keybind_time to the current time at the start of the program
    last_keybind_time = time.time()  # Initialize the keybind time to the current time


    """Camera preparation"""
    cap = cv.VideoCapture(cap_device)
    if not cap.isOpened():
        logger.error("Error: Unable to open the camera.")
        return
    
    cap.set(cv.CAP_PROP_FRAME_WIDTH, cap_width)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, cap_height)
    print(cap_device, cap_width, cap_height)


    """Model Loading"""
    model = load_model('keypoint_classifier_demo_2.keras')
    
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=use_static_image_mode,
        max_num_hands=1,
        min_detection_confidence=min_detection_confidence,
        min_tracking_confidence=min_tracking_confidence,
    )

    # keypoint_classifier = KeyPointClassifier()


    """Read Labels"""
    with open('keypoint_classifier_label_2.csv',encoding='utf-8') as file:
        keypoint_classifier_labels = csv.reader(file)
        keypoint_classifier_labels = [row[0] for row in keypoint_classifier_labels] 

    """Fps Measurement"""
    cvFpsCalc = CvFpsCalc(buffer_len=10)

    # mode = 0
    # recCount = 0
    # csv_path = 'new_keypoint_2.csv'



    while True:
        fps = cvFpsCalc.get()

        """Process Key (ESC: end)"""
        key = cv.waitKey(10)
        if key == 27:  # ESC
            break
        
        """ k -> mode = 1"""
        # number, mode, prediction_enabled = select_mode(key, mode, prediction_enabled)

        # if mode == 1 and recCount == 0:
        #     # Check if the CSV file exists
        #     if os.path.exists(csv_path) and os.path.getsize(csv_path) == 0:# Check if file exists but does not have column to parse:
        #         # If the file exists but is empty, delete the file in local storage
        #         os.remove(csv_path)
        #     elif os.path.exists(csv_path):
        #         # If the file exists, read it into the DataFrame
        #         df = pd.read_csv(csv_path, header=None)
        #     else:
        #         # If the file doesn't exist, create an empty DataFrame with appropriate columns
        #         # Assuming your CSV has a structure with columns like: [label, x1, y1, x2, y2, ..., xn, yn]
        #         columns = [0] + [i for i in range(21)] + [j for j in range(21)]  # Example for 21 landmarks
        #         df = pd.DataFrame(columns=columns)
        #         # Optionally, save the empty DataFrame to the CSV file
        #         df.to_csv(csv_path, index=False)


        """Camera capture"""
        while not shutdown_event.is_set():  # Check for shutdown signal
            ret, image = cap.read()
            if not ret:
                break
            image = cv.flip(image, 1) # Mirror display ()
            debug_image = copy.deepcopy(image)


            if prediction_enabled:
                """Detection implementation"""
                
                image = cv.cvtColor(image, cv.COLOR_BGR2RGB)

                image.flags.writeable = False
                results = hands.process(image)
                image.flags.writeable = True # drawing the landmarks or connections back onto the image once the detection has been completed

                """Visualization"""
                if results.multi_hand_landmarks is not None:
                    for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                        
                        # Bounding Box calculation
                        brect = calc_bounding_rect(debug_image, hand_landmarks)

                        # Landmark calculation
                        Landmark_list = calc_landmark_list(debug_image, hand_landmarks)

                        # Conversion to relative coordinates / normalized coordinates
                        pre_processed_landmark_list = pre_process_landmark(Landmark_list)

                        # Hand sign classification
                        
                        # hand_sign_id, confidence = keypoint_classifier.predict(pre_processed_landmark_list)
                        pred = model.predict(np.array([pre_processed_landmark_list]), verbose=0)
                        hand_sign_id = np.argmax(pred)
                        confidence_percentage = np.ceil(pred[0][hand_sign_id] * 100)


                        # Mark as 'Unknown' if confidence is below 90%
                        if confidence_percentage < 80:
                            hand_sign_text = "Unknown"
                        else:
                            hand_sign_text = keypoint_classifier_labels[hand_sign_id]

                        # Drawing part
                        debug_image = draw_bounding_rect(use_brect, debug_image, brect)
                        debug_image = draw_landmarks(debug_image, Landmark_list)
                        debug_image = draw_info_text(
                            debug_image,
                            brect,
                            handedness,
                            hand_sign_text,
                            confidence_percentage
                        )

                        # Activate keybind if necessary (with delay)
                        last_keybind_time = keybind(hand_sign_text, last_keybind_time)  # Update the keybind time

            # debug_image = draw_point_history(debug_image, point_history)
            cv.putText(debug_image, "FPS:" + str(fps), (10, 30), cv.FONT_HERSHEY_SIMPLEX,1.0, (255, 255, 255), 3, cv.LINE_AA)


            # Display Rendered Image
            # cv.imshow('Hand Gesture Recognition', debug_image)

            _, buffer = cv2.imencode('.jpg', debug_image)
            frame = buffer.tobytes()
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()
    cv2.destroyAllWindows()



def run_flask():
    logger.info("Starting Flask server...")
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)

def signal_handler(signum, frame):
    logger.info(f"Signal {signum} received. Initiating shutdown...")
    shutdown_event.set()  # Trigger shutdown event

if __name__ == '__main__':
    # Set Signal Handlers for Graceful Shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start Flask Server in a Separate Thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    logger.info("Main thread is waiting for shutdown signal.")
    try:
        while not shutdown_event.is_set():
            time.sleep(0.1)  # Prevent busy-waiting
    finally:
        logger.info("Shutting down application...")
        flask_thread.join()  # Ensure Flask thread terminates