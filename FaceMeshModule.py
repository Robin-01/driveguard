import cv2 as cv
import mediapipe as mp


class FaceMeshGenerator:
    """
    A class to generate a facemesh on a video output
    """

    # Initializes FaceMeshGenerator
    def __init__(self, mode=False, num_faces=2, min_detection_con=0.5, min_track_con=0.5):
        """
        Initialize FaceMesh detector with specified parameters

        :param bool mode: Static or video mode
        :param int num_faces: Max number of faces
        :param float min_detection_con: Minimum confidence threshold for face detect
        :param float min_trac_con: Maximum confidence threshold for face detect

        :raises Runtime Error: In case of failed generation of Face Mesh
        """
        try:
            self.results = None
            self.mode = mode
            self.num_faces = num_faces
            self.min_detection_con = min_detection_con
            self.min_track_con = min_track_con

            self.mp_faceDetector = mp.solutions.face_mesh # Gets MediaPipe's face mesh solution module
            
            # Creates FaceMesh object with the parameters
            self.face_mesh = self.mp_faceDetector.FaceMesh(
                static_image_mode=self.mode,
                max_num_faces=self.num_faces,
                min_detection_confidence=self.min_detection_con,
                min_tracking_confidence=self.min_track_con
            )

            self.mp_Draw = mp.solutions.drawing_utils # Gets drawing utils from MediaPipe to visualize landmarks
            self.drawSpecs = self.mp_Draw.DrawingSpec(thickness=1, circle_radius=2) # Creates landmark drawing specifications
        except Exception as e:
            raise RuntimeError(f"Failed to initialize FaceMeshGenerator: {str(e)}") # In case of failed initialization


    # Processes a video frame and generates face mesh landmarks
    def create_face_mesh(self, frame, draw=True):
        """
        Create face mesh landmarks for the given frame

        :param frame: Frame of video to process
        :param draw: Whether or not to draw face mesh on frame

        :return tuple frame, landmarks_dict: processed frame and dictionary of landmarks
        :raises ValueError: No input frame
        :raises Runtime Error: Error processing the frame
        """
        if frame is None:
            raise ValueError("Input frame cannot be None") # In case of no frame

        try:
            frame_rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB) # Converts frame from OpenCV BGR colors to RGB
            self.results = self.face_mesh.process(frame_rgb) # Detects face landmarks using MediaPipe
            landmarks_dict = {} # Emtpy dict of face landmarks

            # Checks to see if face landmarks detected
            if self.results.multi_face_landmarks:
                for face_lms in self.results.multi_face_landmarks: # Iterates through each face landmark
                    if draw:
                        # Draws face mesh contours
                        self.mp_Draw.draw_landmarks(
                            frame, # Specified frame
                            face_lms, # Landmarks
                            self.mp_faceDetector.FACEMESH_CONTOURS, # Contour connections for face mesh
                            self.drawSpecs, # Draw specs for landmarks
                            self.drawSpecs # Draw specs for connections
                        )

                    # Convert normalized landmarks to pixel coordinates (frame dimentions height/width)
                    ih, iw, _ = frame.shape
                    # Loops through each landmark point by ID
                    for ID, lm in enumerate(face_lms.landmark):
                        x, y = int(lm.x * iw), int(lm.y * ih) # Convert normalized coordinate to pixel coordinate
                        landmarks_dict[ID] = (x, y) # Adds coordinate to dictionary under landmark ID

            return frame, landmarks_dict # Returns frame and dictionary of coordinates
        except Exception as e:
            raise RuntimeError(f"Error processing frame: {str(e)}") # In case of error processing frame