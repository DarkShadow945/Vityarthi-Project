import time

TOO_CLOSE_LIMIT = 40
LITTLE_CLOSE_LIMIT = 50
SAFE_MAX_LIMIT = 70

RECOMMENDED_RANGE_TEXT = "50 - 70 cm"

WARNING_HOLD_SECONDS = 3.0

SMOOTHING_WINDOW = 8


def now():
    return time.time()


def format_seconds_to_minutes(seconds):
    minutes = int(seconds // 60)
    return f"{minutes} min"


def try_system_beep():
    try:
        import winsound
        winsound.Beep(1000, 200)
    except Exception:
        try:
            print("\a", end="")
        except Exception:
            pass