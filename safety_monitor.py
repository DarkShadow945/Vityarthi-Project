from utils import (
    TOO_CLOSE_LIMIT,
    LITTLE_CLOSE_LIMIT,
    SAFE_MAX_LIMIT,
    WARNING_HOLD_SECONDS,
    now,
)

# Status labels used everywhere in the app
STATUS_TOO_CLOSE = "TOO CLOSE"
STATUS_LITTLE_CLOSE = "A LITTLE CLOSE"
STATUS_SAFE = "SAFE"
STATUS_TOO_FAR = "TOO FAR / NORMAL"
STATUS_UNKNOWN = "NO FACE DETECTED"


def classify_distance(distance_cm):
    if distance_cm is None:
        return STATUS_UNKNOWN

    if distance_cm < TOO_CLOSE_LIMIT:
        return STATUS_TOO_CLOSE
    elif distance_cm < LITTLE_CLOSE_LIMIT:
        return STATUS_LITTLE_CLOSE
    elif distance_cm <= SAFE_MAX_LIMIT:
        return STATUS_SAFE
    else:
        return STATUS_TOO_FAR


class SafetyMonitor:

    def __init__(self):
        self.too_close_start_time = None
        self.warning_active = False

    def evaluate(self, distance_cm):
        status = classify_distance(distance_cm)
        should_warn = False

        if status == STATUS_TOO_CLOSE:
            if self.too_close_start_time is None:
                self.too_close_start_time = now()
                self.warning_active = False
            else:
                elapsed = now() - self.too_close_start_time
                if elapsed >= WARNING_HOLD_SECONDS and not self.warning_active:
                    should_warn = True
                    self.warning_active = True
        else:
            self.too_close_start_time = None
            self.warning_active = False

        return status, should_warn