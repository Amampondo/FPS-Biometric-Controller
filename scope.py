import cv2
import mediapipe as mp
import math

# Define indices for eye landmarks
LEFT_EYE_POINTS = [33, 160, 158, 133, 153, 144]
RIGHT_EYE_POINTS = [362, 385, 387, 263, 373, 380]

# Define EAR threshold for blink detection
EAR_THRESHOLD = 0.3

class Scope:
    
    def __init__(self,load):

        # Initialize MediaPipe face mesh model
        self._mp_face_mesh =  mp.solutions.face_mesh
        self._mp_drawing =  mp.solutions.drawing_utils

        # Create an instance of the FaceMesh class
        self._face_mesh =  self._mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.8)
        self._load = load

    def zoom(self):
        
        self._load.zoom()
        
    def calculate_ear(self,eye_landmarks):
        """Calculate the Eye Aspect Ratio (EAR)."""
        # Get vertical distances
        A = math.sqrt((eye_landmarks[1][0] - eye_landmarks[5][0])**2 + (eye_landmarks[1][1] - eye_landmarks[5][1])**2)
        B = math.sqrt((eye_landmarks[2][0] - eye_landmarks[4][0])**2 + (eye_landmarks[2][1] - eye_landmarks[4][1])**2)

        # Get horizontal distance
        C = math.sqrt((eye_landmarks[0][0] - eye_landmarks[3][0])**2 + (eye_landmarks[0][1] - eye_landmarks[3][1])**2)

        # Compute EAR
        ear = (A + B) / (2.0 * C)
        return ear

    def draw_eye_landmarks(self,image, landmarks, eye_points):
        """Draw eye landmarks on the image."""
        for idx in eye_points:
            landmark = landmarks[idx]
            x = int(landmark.x * image.shape[1])
            y = int(landmark.y * image.shape[0])
            cv2.circle(image, (x, y), 2, (0, 255, 0), -1)  # Draw the eye landmark

    def zoom_into_frame(self,frame, zoom_factor=1.5, center=None):
        """
        Zoom into a specific region of the frame.

        Parameters:
        - frame: The input frame (image) from which to zoom in.
        - zoom_factor: The factor by which to zoom into the frame. Must be greater than 1.
        - center: The (x, y) coordinates of the center point for zooming. If None, the center of the frame is used.

        Returns:
        - zoomed_frame: The zoomed-in frame.
        """
        height, width = frame.shape[:2]
        
        # Default center to the center of the frame if not provided
        if center is None:
            center = (width // 2, height // 2)
        
        x_center, y_center = center
        
        # Calculate the zoomed-in region
        radius_x = int(width / (2 * zoom_factor))
        radius_y = int(height / (2 * zoom_factor))
        
        # Compute the bounding box for the zoomed-in region
        x1 = max(x_center - radius_x, 0)
        x2 = min(x_center + radius_x, width)
        y1 = max(y_center - radius_y, 0)
        y2 = min(y_center + radius_y, height)
        
        # Crop the region of interest from the frame
        cropped_frame = frame[y1:y2, x1:x2]
        
        # Resize the cropped frame to the original frame size
        zoomed_frame = cv2.resize(cropped_frame, (width, height), interpolation=cv2.INTER_LINEAR)
        
        return zoomed_frame

    def detect(self,frame2):

            # Convert the image color from BGR to RGB
            rgb_frame = cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB)

            # Process the image and get face landmarks
            results = self._face_mesh.process(rgb_frame)
            
            isZoom = False

            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    landmarks = [(lm.x, lm.y) for lm in face_landmarks.landmark]

                    # Extract eye landmarks
                    left_eye_landmarks = [landmarks[i] for i in LEFT_EYE_POINTS]
                    right_eye_landmarks = [landmarks[i] for i in RIGHT_EYE_POINTS]

                    # Calculate EAR for both eyes
                    left_ear = self.calculate_ear(left_eye_landmarks)
                    right_ear = self.calculate_ear(right_eye_landmarks)

                    # Check for blink
                    if left_ear < EAR_THRESHOLD and right_ear < EAR_THRESHOLD:
                        cv2.putText(frame2, "Zoom in", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                        isZoom = True

                    # Draw eye landmarks
                    self.draw_eye_landmarks(frame2, face_landmarks.landmark, LEFT_EYE_POINTS)
                    self.draw_eye_landmarks(frame2, face_landmarks.landmark, RIGHT_EYE_POINTS)
                    
                    if left_ear < EAR_THRESHOLD and right_ear < EAR_THRESHOLD:
                        
                        left_ear = self.calculate_ear(left_eye_landmarks)
                        
                        isZoom = True
                        

            # Display the resulting frame
            return frame2 , isZoom