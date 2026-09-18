# Screen Distance Safety Monitor

Screen Distance Safety Monitor is a Python-based desktop application designed to help promote healthy viewing habits by tracking how far you sit from your computer screen. 

Using your webcam and Google's MediaPipe facial recognition technology, the app estimates your distance from the screen in real-time, provides visual status indicators, sounds an alarm if you lean in too close for too long, and tracks your session statistics.

## Features

*   **Real-Time Distance Estimation**: Calculates your approximate distance from the screen using webcam geometry and facial detection.
*   **Live Video Feedback**: Displays a mirrored camera feed with a bounding box around your face and the current distance overlay.
*   **Safety Status Indicators**: Categorizes your distance into zones: `TOO CLOSE`, `A LITTLE CLOSE`, `SAFE`, and `TOO FAR / NORMAL`.
*   **Auditory Warnings**: Triggers a system beep if you remain in the "TOO CLOSE" zone for more than 3 seconds.
*   **Session Tracking**: Monitors your session duration, average/min/max distances, and total number of warnings.
*   **Report Generation**: Exports your session data into easily readable `.txt` summary reports and `.csv` raw data logs for personal tracking.
*   **Automatic Model Setup**: Automatically downloads the required MediaPipe Face Detection model on the first run.

## Prerequisites

*   **Python:** Version 3.7 or higher.
*   **Webcam:** Required for tracking and distance estimation.

## Installation

1.  **Clone or Download the Repository:**
    Ensure all provided Python scripts (`main.py`, `gui.py`, etc.) are in the same directory.

2.  **Install Dependencies:**
    Open your terminal or command prompt, navigate to the project folder, and install the required Python packages using:
    ```bash
    pip install -r requirements.txt
    ```
    *The `requirements.txt` file includes `opencv-python`, `mediapipe`, `Pillow`, and `numpy`.*

## Usage

1.  **Launch the Application:**
    Run the main script from your terminal:
    ```bash
    python main.py
    ```
    *(Note: On the very first run, the app will automatically download the `blaze_face_short_range.tflite` model into a `models/` folder.)*

2.  **Controls:**
    *   **Start Camera:** Initializes your webcam and begins face detection/distance estimation.
    *   **Start Monitoring:** Begins recording session statistics and enables auditory warnings.
    *   **Stop Monitoring / Stop Camera:** Halts tracking and turns off the camera feed.
    *   **Reset Session:** Clears the current session's data (warnings, duration, and distance history).
    *   **Save Report:** Generates and saves a `.txt` summary and a `.csv` log of the current session into a `reports/` folder.

## Project Structure

*   `main.py`: The entry point of the application.
*   `gui.py`: Manages the Tkinter graphical user interface, layout, and video rendering.
*   `camera.py`: Handles webcam initialization, frame capturing, and horizontal flipping.
*   `face_detector.py`: Integrates MediaPipe to detect faces and compute bounding boxes. Downloads the model on first run.
*   `distance_estimator.py`: Calculates distance based on perceived face width and focal length geometry. Includes a rolling average for jitter smoothing.
*   `safety_monitor.py`: Evaluates the current distance against safe thresholds and triggers warnings.
*   `session_tracker.py`: Stores historical distance data and calculates averages, mins, maxes, and duration.
*   `report_generator.py`: Formats and saves session data into `.txt` and `.csv` files.
*   `utils.py`: Contains shared constants (thresholds, smoothing windows) and helper functions.

## Disclaimer

**Not a Medical Device:** The distance calculated by this application is an approximate estimate based on an assumed average human face width (14 cm) and standard webcam focal length. It is not a precise medical measurement tool and should only be used as a general awareness tool for screen ergonomics.