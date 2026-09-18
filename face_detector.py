import os
import urllib.request

import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_tasks
from mediapipe.tasks.python import vision as mp_vision

MODEL_FOLDER = "models"
MODEL_FILENAME = "blaze_face_short_range.tflite"
MODEL_PATH = os.path.join(MODEL_FOLDER, MODEL_FILENAME)

# Official Google-hosted model file for MediaPipe's short-range face detector.
MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/face_detector/"
    "blaze_face_short_range/float16/1/blaze_face_short_range.tflite"
)


def _ensure_model_downloaded():
    if os.path.exists(MODEL_PATH):
        return

    os.makedirs(MODEL_FOLDER, exist_ok=True)
    print("Downloading face detection model (first run only)...")
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
    print("Model downloaded to", MODEL_PATH)


class FaceDetector:

    def __init__(self, min_detection_confidence=0.6):
        _ensure_model_downloaded()

        base_options = mp_tasks.BaseOptions(model_asset_path=MODEL_PATH)
        options = mp_vision.FaceDetectorOptions(
            base_options=base_options,
            min_detection_confidence=min_detection_confidence,
        )
        self.detector = mp_vision.FaceDetector.create_from_options(options)

    def detect(self, frame_bgr):
        rgb_frame = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        result = self.detector.detect(mp_image)

        result_info = {"face_found": False, "multiple_faces": False, "box": None}

        if not result.detections:
            return result_info

        frame_height, frame_width, _ = frame_bgr.shape
        boxes = []

        for detection in result.detections:
            bbox = detection.bounding_box
            x, y = max(0, bbox.origin_x), max(0, bbox.origin_y)
            w, h = max(0, bbox.width), max(0, bbox.height)
            w = min(w, frame_width - x)
            h = min(h, frame_height - y)
            boxes.append((x, y, w, h))

        result_info["face_found"] = True
        result_info["multiple_faces"] = len(boxes) > 1

        largest_box = max(boxes, key=lambda b: b[2] * b[3])
        result_info["box"] = largest_box

        return result_info

    def close(self):
        self.detector.close()