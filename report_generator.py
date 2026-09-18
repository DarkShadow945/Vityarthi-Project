import os
import csv
from datetime import datetime
from utils import format_seconds_to_minutes, RECOMMENDED_RANGE_TEXT

REPORTS_FOLDER = "reports"


def _ensure_reports_folder_exists():
    if not os.path.exists(REPORTS_FOLDER):
        os.makedirs(REPORTS_FOLDER)


def build_report_text(session_tracker):
    duration_text = format_seconds_to_minutes(session_tracker.get_session_duration_seconds())
    avg = session_tracker.get_average_distance()
    min_d = session_tracker.get_min_distance()
    max_d = session_tracker.get_max_distance()

    lines = [
        "Screen Distance Safety Monitor Report",
        "=" * 40,
        f"Generated On       : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Session Duration   : {duration_text}",
        f"Recommended Range  : {RECOMMENDED_RANGE_TEXT}",
        f"Average Distance   : {avg if avg is not None else 'N/A'} cm",
        f"Minimum Distance   : {min_d if min_d is not None else 'N/A'} cm",
        f"Maximum Distance   : {max_d if max_d is not None else 'N/A'} cm",
        f"Warning Count      : {session_tracker.warning_count}",
        f"Overall Status     : {session_tracker.get_overall_status()}",
        "",
        "Note: Distance values are approximate estimates based on webcam",
        "face-size geometry. This is not a medical measurement and should",
        "only be used as a general screen-distance awareness tool.",
    ]
    return "\n".join(lines)


def save_txt_report(session_tracker, filename=None):
    _ensure_reports_folder_exists()
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"session_report_{timestamp}.txt"

    filepath = os.path.join(REPORTS_FOLDER, filename)
    with open(filepath, "w") as f:
        f.write(build_report_text(session_tracker))

    return filepath


def save_csv_report(session_tracker, filename=None):
    _ensure_reports_folder_exists()
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"session_readings_{timestamp}.csv"

    filepath = os.path.join(REPORTS_FOLDER, filename)
    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["reading_number", "distance_cm"])
        for i, distance in enumerate(session_tracker.distance_readings, start=1):
            writer.writerow([i, distance])

    return filepath