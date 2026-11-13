
import cv2


def create_tracker():

    if hasattr(cv2, "TrackerCSRT_create"):
        return cv2.TrackerCSRT_create()

    if hasattr(cv2, "legacy"):
        return cv2.legacy.TrackerCSRT_create()

    raise RuntimeError(
        "CSRT tracker unavailable. Install opencv-contrib-python."
    )


def initialize_tracker(frame, bbox):

    tracker = create_tracker()

    success = tracker.init(
        frame,
        tuple(map(int, bbox))
    )

    if success is False:
        raise RuntimeError("Failed to initialize face tracker")

    return tracker


def update_tracker(tracker, frame):

    success, bbox = tracker.update(frame)

    if not success:
        return None

    x, y, w, h = map(int, bbox)

    return x, y, w, h
