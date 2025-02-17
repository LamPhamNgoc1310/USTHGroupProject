from tensorflow.keras.models import load_model
import mediapipe as mp
from keypoint_classifier_draft2 import KeyPointClassifier
from CvFpsCalc import CvFpsCalc
from functions import *
import cv2 as cv
import copy
import os
import pandas as pd

def main():
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

    mode = 0
    recCount = 0
    csv_path = 'new_keypoint_2.csv'
    
    
    while True:
        if recCount == 500: 
            recCount = 0
            mode = 0
        
        fps = cvFpsCalc.get()

        """Process Key (ESC: end)"""
        key = cv.waitKey(10)
        if key == 27:  # ESC
            break
        
        """ k -> mode = 1"""
        number, mode, prediction_enabled = select_mode(key, mode, prediction_enabled)

        if mode == 1 and recCount == 0:
            # Check if the CSV file exists
            if os.path.exists(csv_path) and os.path.getsize(csv_path) == 0:# Check if file exists but does not have column to parse:
                # If the file exists but is empty, delete the file in local storage
                os.remove(csv_path)
            elif os.path.exists(csv_path):
                # If the file exists, read it into the DataFrame
                df = pd.read_csv(csv_path, header=None)
            else:
                # If the file doesn't exist, create an empty DataFrame with appropriate columns
                # Assuming your CSV has a structure with columns like: [label, x1, y1, x2, y2, ..., xn, yn]
                columns = [0] + [i for i in range(21)] + [j for j in range(21)]  # Example for 21 landmarks
                df = pd.DataFrame(columns=columns)
                # Optionally, save the empty DataFrame to the CSV file
                df.to_csv(csv_path, index=False)


        """Camera capture"""
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

                    # Write to the dataset file
                    if mode == 1 and recCount < 500:
                        # Create a new number for the current entry (e.g., based on the max label in the CSV)
                        number = df[0].max() + 1 if not df.empty else 0
                        recCount += 1
                        cv.putText(debug_image, 'hand record activated', (10, 70), cv.FONT_HERSHEY_SIMPLEX, 1.3, (0, 255, 0), 3)
                        print(f"Mode: {mode}, Observation: {recCount}, Label: {number}")
                        # Write to the dataset file
                        logging_csv(number, pre_processed_landmark_list)
                        # Store labels in 'keypoint_classifier_label_new.csv'
                        store_labels_to_new_file('new_keypoint_2.csv', 'keypoint_classifier_label_2.csv')

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
        debug_image = draw_info(debug_image, fps, mode, number)

        # Display Rendered Image
        cv.imshow('Hand Gesture Recognition', debug_image)

    cap.release()
    cv.destroyAllWindows()


if __name__ == '__main__':
    main()