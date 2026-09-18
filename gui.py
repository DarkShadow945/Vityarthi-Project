import tkinter as tk
from tkinter import messagebox
import cv2
from PIL import Image, ImageTk

from camera import Camera
from face_detector import FaceDetector
from distance_estimator import DistanceEstimator
from safety_monitor import SafetyMonitor, STATUS_TOO_CLOSE, STATUS_UNKNOWN
from session_tracker import SessionTracker
from report_generator import save_txt_report, save_csv_report
from utils import RECOMMENDED_RANGE_TEXT, try_system_beep, format_seconds_to_minutes

# Colors used for the status label (kept minimal, as requested)
STATUS_COLORS = {
    "TOO CLOSE": "#d9362e",
    "A LITTLE CLOSE": "#e0a11c",
    "SAFE": "#2e9e4c",
    "TOO FAR / NORMAL": "#4a6fa5",
    "NO FACE DETECTED": "#777777",
}

VIDEO_WIDTH = 640
VIDEO_HEIGHT = 480
FRAME_DELAY_MS = 20

class ScreenDistanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Screen Distance Safety Monitor")
        self.root.configure(bg="#f4f6f8")
        self.root.resizable(False, False)

        self.camera = Camera()
        self.face_detector = FaceDetector()
        self.distance_estimator = DistanceEstimator()
        self.safety_monitor = SafetyMonitor()
        self.session_tracker = SessionTracker()

        self.camera_running = False
        self.monitoring_active = False

        self._build_layout()
        self._update_loop()

    def _build_layout(self):
        header = tk.Label(
            self.root,
            text="Screen Distance Safety Monitor",
            font=("Segoe UI", 18, "bold"),
            bg="#f4f6f8",
            fg="#1f2937",
            pady=10,
        )
        header.grid(row=0, column=0, columnspan=2, sticky="w", padx=15)

        self.video_label = tk.Label(self.root, bg="black", width=VIDEO_WIDTH, height=VIDEO_HEIGHT)
        self.video_label.grid(row=1, column=0, padx=15, pady=10)

        info_frame = tk.Frame(self.root, bg="#ffffff", bd=1, relief="solid", padx=15, pady=15)
        info_frame.grid(row=1, column=1, padx=(0, 15), pady=10, sticky="n")

        self.info_labels = {}
        info_fields = [
            ("distance", "Current Distance:"),
            ("recommended", "Recommended:"),
            ("status", "Status:"),
            ("average", "Average Distance:"),
            ("warnings", "Warnings:"),
            ("duration", "Session:"),
        ]

        for i, (key, label_text) in enumerate(info_fields):
            tk.Label(info_frame, text=label_text, font=("Segoe UI", 11, "bold"),
                     bg="#ffffff", anchor="w").grid(row=i, column=0, sticky="w", pady=6)
            value_label = tk.Label(info_frame, text="--", font=("Segoe UI", 11),
                                    bg="#ffffff", anchor="w")
            value_label.grid(row=i, column=1, sticky="w", padx=(10, 0))
            self.info_labels[key] = value_label

        self.info_labels["recommended"].config(text=RECOMMENDED_RANGE_TEXT)

        disclaimer = tk.Label(
            info_frame,
            text="Note: Distance is an approximate estimate,\nnot a medical measurement.",
            font=("Segoe UI", 8, "italic"),
            bg="#ffffff", fg="#888888", justify="left"
        )
        disclaimer.grid(row=len(info_fields), column=0, columnspan=2, sticky="w", pady=(10, 0))

        # --- Buttons ---
        button_frame = tk.Frame(self.root, bg="#f4f6f8")
        button_frame.grid(row=2, column=0, columnspan=2, pady=15)

        button_style = {"font": ("Segoe UI", 10), "width": 16, "padx": 4, "pady": 6}

        tk.Button(button_frame, text="Start Camera", command=self.start_camera, **button_style).grid(row=0, column=0, padx=4)
        tk.Button(button_frame, text="Stop Camera", command=self.stop_camera, **button_style).grid(row=0, column=1, padx=4)
        tk.Button(button_frame, text="Start Monitoring", command=self.start_monitoring, **button_style).grid(row=0, column=2, padx=4)
        tk.Button(button_frame, text="Stop Monitoring", command=self.stop_monitoring, **button_style).grid(row=0, column=3, padx=4)
        tk.Button(button_frame, text="Reset Session", command=self.reset_session, **button_style).grid(row=1, column=0, padx=4, pady=6)
        tk.Button(button_frame, text="Save Report", command=self.save_report, **button_style).grid(row=1, column=1, padx=4, pady=6)
        tk.Button(button_frame, text="Exit", command=self.exit_app, **button_style).grid(row=1, column=2, padx=4, pady=6)

    def start_camera(self):
        if self.camera_running:
            return
        success, message = self.camera.start()
        if not success:
            messagebox.showerror("Camera Error", message)
            return
        self.camera_running = True

    def stop_camera(self):
        self.camera_running = False
        self.monitoring_active = False
        self.camera.stop()
        self.video_label.config(image="", bg="black")

    def start_monitoring(self):
        if not self.camera_running:
            messagebox.showwarning("Camera Not Started", "Please start the camera first.")
            return
        self.monitoring_active = True
        self.session_tracker.start_monitoring()

    def stop_monitoring(self):
        self.monitoring_active = False
        self.session_tracker.stop_monitoring()

    def reset_session(self):
        self.session_tracker.reset()
        self.distance_estimator.reset()
        self.safety_monitor = SafetyMonitor()

    def save_report(self):
        txt_path = save_txt_report(self.session_tracker)
        csv_path = save_csv_report(self.session_tracker)
        messagebox.showinfo(
            "Report Saved",
            f"Report saved successfully:\n\n{txt_path}\n{csv_path}",
        )

    def exit_app(self):
        self.stop_camera()
        self.face_detector.close()
        self.root.destroy()

    def _update_loop(self):
        if self.camera_running:
            self._process_one_frame()
        self.root.after(FRAME_DELAY_MS, self._update_loop)

    def _process_one_frame(self):
        success, frame = self.camera.read_frame()
        if not success:
            return

        detection = self.face_detector.detect(frame)

        distance = None
        status_text = STATUS_UNKNOWN

        if detection["multiple_faces"]:
            status_text = "MULTIPLE FACES DETECTED"
            cv2.putText(frame, "Multiple faces detected", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        elif detection["face_found"]:
            x, y, w, h = detection["box"]
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 200, 0), 2)

            distance = self.distance_estimator.get_smoothed_distance(w)
            status_text, should_warn = self.safety_monitor.evaluate(distance)

            cv2.putText(frame, f"{distance} cm", (x, max(0, y - 10)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            if self.monitoring_active:
                self.session_tracker.record_distance(distance)
                if should_warn:
                    self.session_tracker.record_warning()
                    try_system_beep()
        else:
            cv2.putText(frame, "Face not detected", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        self._render_frame(frame)
        self._update_info_panel(distance, status_text)

    def _render_frame(self, frame_bgr):
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        frame_rgb = cv2.resize(frame_rgb, (VIDEO_WIDTH, VIDEO_HEIGHT))
        image = Image.fromarray(frame_rgb)
        photo = ImageTk.PhotoImage(image=image)

        self.video_label.imgtk = photo  # keep a reference or it gets garbage collected
        self.video_label.configure(image=photo)

    def _update_info_panel(self, distance, status_text):
        self.info_labels["distance"].config(text=f"{distance} cm" if distance else "--")
        self.info_labels["status"].config(
            text=status_text,
            fg=STATUS_COLORS.get(status_text, "#000000"),
        )

        avg = self.session_tracker.get_average_distance()
        self.info_labels["average"].config(text=f"{avg} cm" if avg else "--")
        self.info_labels["warnings"].config(text=str(self.session_tracker.warning_count))
        self.info_labels["duration"].config(
            text=format_seconds_to_minutes(self.session_tracker.get_session_duration_seconds())
        )