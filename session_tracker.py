from utils import now


class SessionTracker:

    def __init__(self):
        self.reset()

    def reset(self):
        self.start_time = now()
        self.distance_readings = []
        self.warning_count = 0
        self.is_monitoring = False

    def start_monitoring(self):
        self.is_monitoring = True
        if self.start_time is None:
            self.start_time = now()

    def stop_monitoring(self):
        self.is_monitoring = False

    def record_distance(self, distance_cm):
        if distance_cm is not None:
            self.distance_readings.append(distance_cm)

    def record_warning(self):
        self.warning_count += 1

    def get_average_distance(self):
        if not self.distance_readings:
            return None
        return round(sum(self.distance_readings) / len(self.distance_readings), 1)

    def get_min_distance(self):
        if not self.distance_readings:
            return None
        return round(min(self.distance_readings), 1)

    def get_max_distance(self):
        if not self.distance_readings:
            return None
        return round(max(self.distance_readings), 1)

    def get_session_duration_seconds(self):
        return now() - self.start_time

    def get_overall_status(self):
        avg = self.get_average_distance()
        if avg is None:
            return "No Data"

        if self.warning_count == 0:
            return "Mostly Safe"
        elif self.warning_count <= 3:
            return "Occasionally Too Close"
        else:
            return "Frequently Too Close - Consider Adjusting Your Setup"