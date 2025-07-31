import numpy as np
import cv2 as cv
from FaceMeshModule import FaceMeshGenerator
from sleep_database import SleepDatabase
from micro_connection import MicroConnection
import threading


class SleepDetector:
    """
    A class to detect sleep occurrences in a video using facial landmarks.
    
    This class processes video input to detect eye status by calculating the Eye Aspect Ratio (EAR)
    of both eyes.
    """

    # Initialize SleepDetector
    def __init__(self, video_path, ear_threshold, consec_frames, asleep, database=None):
        """
        Initialize the SleepDetector with its variable attributes
        
        :param int video_path: The default webcam/camera of the computer
        :param float ear_threshold: Threshold of which eyes are considered closed
        :param int consec_frames: The amount of consecutive frames below the ear threshold to be considered asleep
        :param bool asleep: Whether or not the person is asleep
        :param class database: Connects to an instance of the SleepDatabase class

        :return None
        """
        # Initialize face mesh detector
        self.generator = FaceMeshGenerator() 
        self.video_path = video_path

        # Initialize provided database or create new one
        self.database = database if database else SleepDatabase()

        # Initialize connection to the Adafruit microcontroller
        self.microcontroller = MicroConnection()
        
        # Define facial landmarks for eye detection
        # Each list contains indices corresponding to points around the eyes
        self.RIGHT_EYE = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
        self.LEFT_EYE = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
        
        # Specific landmarks for EAR calculation
        # These specific points are used to calculate the eye aspect ratio
        self.RIGHT_EYE_EAR = [33, 159, 158, 133, 153, 145]
        self.LEFT_EYE_EAR = [362, 380, 374, 263, 386, 385]
        
        # Sleep detection parameters
        self.ear_threshold = ear_threshold  # Eye aspect ratio threshold for blink detection
        self.consec_frames = consec_frames  # Minimum consecutive frames for a valid blink
        self.frame_counter = 0    # Counter for consecutive frames below threshold
        self.asleep = asleep
        
        # Define colors for visualization (in BGR format)
        self.GREEN_COLOR = (86, 241, 13)  # Used when eyes are open
        self.RED_COLOR = (30, 46, 209)    # Used when eyes are closed


    # Checks if the person is asleep, upload timestamp and create warning if true
    def check_asleep(self, ear):
        """
        Determines if the person is asleep for at least 90 frames and takes a timestamp/creates a warning if true

        :param float ear: The current eye aspect ratio

        :return None
        """
        # When ear is past the threshold (eyes closed)
        if ear < self.ear_threshold:
            self.frame_counter += 1
            if self.frame_counter >= self.consec_frames and not self.asleep: # Checks to see if frames for eyes closed is consecutive to count as asleep
                self.database.take_sleep_timestamp() # Uploads sleep timestamp
                self.asleep = True # Changes sleep status
                threading.Thread(target=self.microcontroller.sleep_warning, daemon=True).start() # Runs the led/buzzer on another thread, so camera capture continues
        # When ear is above threshold (eyes open)
        else:
            self.asleep = False # Change sleep status
            self.frame_counter = 0 # Reset frames for eyes closed to 0


    # Calculates the EAR
    def eye_aspect_ratio(self, eye_landmarks, landmarks):
        """
        Calculate the eye aspect ratio (EAR) for given eye landmarks.
        
        The EAR is calculated using the formula:
        EAR = (||p2-p6|| + ||p3-p5||) / (2||p1-p4||)
        where p1-p6 are specific points around the eye.
        
        :param list eye_landmarks: Indices of landmarks for one eye
        :param list landmarks: List of all facial landmarks
        
        :return float: Calculated eye aspect ratio
        """
        A = np.linalg.norm(np.array(landmarks[eye_landmarks[1]]) - np.array(landmarks[eye_landmarks[5]])) # Eye vertical distance 1
        B = np.linalg.norm(np.array(landmarks[eye_landmarks[2]]) - np.array(landmarks[eye_landmarks[4]])) # Eye vertical distance 2
        C = np.linalg.norm(np.array(landmarks[eye_landmarks[0]]) - np.array(landmarks[eye_landmarks[3]])) # Eye width
        return (A + B) / (2.0 * C)


    # Sets mesh landmark visualization colors based on eye state
    def set_colors(self, ear):
        """
        Determine visualization color based on eye aspect ratio (red = closed / green = open)
        
        :param float ear: Current eye aspect ratio
        
        :return tuple: BGR color values
        """
        return self.RED_COLOR if ear < self.ear_threshold else self.GREEN_COLOR


    # Draws landmarks around eyes on the video output
    def draw_eye_landmarks(self, frame, landmarks, eye_landmarks, color):
        """
        Draw landmarks around the eyes on the frame.
        
        :param nump.ndarray frame: Video frame to draw on
        :param list landmarks: List of facial landmarks
        :param list eye_landmarks: Indices of landmarks for one eye
        :param tuple color: BGR color values for drawing

        :return None
        """
        # Loops through each index for eye landmarks
        for loc in eye_landmarks:
            cv.circle(frame, (landmarks[loc]), 4, color, cv.FILLED) # Draws circle on each eye landmark


    # Processes the video and detects asleep
    def process_video(self):
        """
        Main method to process the video and detect sleep status
        
        This method:
        1. Opens the video
        2. Processes each frame to detect faces and calculate EAR
        3. Determines sleep status based on EAR values
        4. Displays the processed video
        5. Uploads to sleep database and creates sleep warning if asleep
        
        :raises IOError: If video file cannot be opened
        :raises Exception: For other processing errors
        """
        try:
            # Open video capture
            cap = cv.VideoCapture(self.video_path)
            if not cap.isOpened():
                print(f"Failed to open video: {self.video_path}")
                raise IOError("Error: couldn't open the video!")

            # Get video properties
            w, h, fps = (int(cap.get(x)) for x in (
                cv.CAP_PROP_FRAME_WIDTH,
                cv.CAP_PROP_FRAME_HEIGHT,
                cv.CAP_PROP_FPS
            ))

            # Main processing loop as long as video is opened
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret: # Break the loop if no frame is read/video ends
                    break

                # Detect facial landmarks
                frame, face_landmarks = self.generator.create_face_mesh(frame, draw=False)

                if len(face_landmarks) > 0:
                    # Calculate eye aspect ratio
                    right_ear = self.eye_aspect_ratio(self.RIGHT_EYE_EAR, face_landmarks)
                    left_ear = self.eye_aspect_ratio(self.LEFT_EYE_EAR, face_landmarks)
                    ear = (right_ear + left_ear) / 2.0

                    # Update blink detection
                    self.check_asleep(ear)

                    # Determine visualization color based on EAR
                    color = self.set_colors(ear)

                    # Draw visualizations
                    self.draw_eye_landmarks(frame, face_landmarks, self.RIGHT_EYE, color)
                    self.draw_eye_landmarks(frame, face_landmarks, self.LEFT_EYE, color)

                    # Display the frame
                    resized_frame = cv.resize(frame, (1280, 720))
                    cv.imshow("DriveGuard", resized_frame)

                # Break loop if 'p' is pressed or window is closed
                if cv.waitKey(int(1000/fps)) & 0xFF == ord('p') or cv.getWindowProperty("DriveGuard", cv.WND_PROP_VISIBLE) < 1:
                    break

            # Cleanup/clear everything once video is closed
            cap.release()
            cv.destroyAllWindows()

        except Exception as e:
            print(f"An error occurred: {e}")


# Allows for testing/usage if python file is run by itself, not imported as a method
if __name__ == "__main__":
    
    # Create sleep detector with parameters
    sleep_detector = SleepDetector(
        video_path=0, # Change number for video path depending on intended webcam
        ear_threshold=0.24, # Calibration for eye detection
        consec_frames=90, # Approximately 3 seconds for sleep
        asleep = False
    )
    sleep_detector.process_video() # Processes video and sleep detection