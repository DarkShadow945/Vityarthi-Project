from collections import deque
from utils import SMOOTHING_WINDOW

KNOWN_FACE_WIDTH_CM = 14.0
DEFAULT_FOCAL_LENGTH_PX = 615.0


class DistanceEstimator:

    def __init__(self, focal_length_px=DEFAULT_FOCAL_LENGTH_PX):
        self.focal_length_px = focal_length_px
        # A short history of recent readings, used to smooth out jitter.
        self.recent_readings = deque(maxlen=SMOOTHING_WINDOW)

    def calculate_raw_distance(self, face_width_px):
        if face_width_px is None or face_width_px <= 0:
            return None

        distance_cm = (KNOWN_FACE_WIDTH_CM * self.focal_length_px) / face_width_px
        return round(distance_cm, 1)

    def get_smoothed_distance(self, face_width_px):
        raw_distance = self.calculate_raw_distance(face_width_px)

        if raw_distance is None:
            return None

        self.recent_readings.append(raw_distance)
        smoothed = sum(self.recent_readings) / len(self.recent_readings)
        return round(smoothed, 1)

    def calibrate(self, face_width_px, known_distance_cm):
        if face_width_px <= 0 or known_distance_cm <= 0:
            return False

        self.focal_length_px = (face_width_px * known_distance_cm) / KNOWN_FACE_WIDTH_CM
        self.recent_readings.clear()
        return True

    def reset(self):
        self.recent_readings.clear()