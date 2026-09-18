import cv2


class Camera:

    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.cap = None
        self.is_running = False

    def start(self):
        self.cap = cv2.VideoCapture(self.camera_index)

        if not self.cap.isOpened():
            self.is_running = False
            return False, "Could not open webcam. It may be unavailable or in use."

        self.is_running = True
        return True, "Camera started successfully."

    def read_frame(self):
        if self.cap is None or not self.is_running:
            return False, None

        success, frame = self.cap.read()
        if not success or frame is None:
            return False, None

        # Flip horizontally so the video feels like a mirror (more natural for users)
        frame = cv2.flip(frame, 1)
        return True, frame

    def stop(self):
        if self.cap is not None:
            self.cap.release()
        self.is_running = False