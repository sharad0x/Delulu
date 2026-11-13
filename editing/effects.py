
import cv2
import numpy as np
import random


def get_effect_bbox(frame, face_bbox):

    x, y, w, h = face_bbox

    # Expand effect region
    new_w = int(w * 1.4)
    new_h = int(h * 10.6)

    # Center around face
    cx = x + w // 2
    cy = y + h // 2

    x1 = max(0, cx - new_w // 2)
    y1 = max(0, cy - new_h // 2)

    x2 = min(frame.shape[1], cx + new_w // 2)
    y2 = min(frame.shape[0], cy + new_h // 2)

    return x1, y1, x2, y2


# ==========================================
# ZOOM
# ==========================================

def apply_zoom(frame, bbox, amount):

    x1, y1, x2, y2 = get_effect_bbox(
        frame, bbox
    )

    roi = frame[y1:y2, x1:x2]

    if roi.size == 0:
        return frame

    rh, rw = roi.shape[:2]

    factor = 1.0 + amount

    new_w = max(1, int(rw / factor))
    new_h = max(1, int(rh / factor))

    cx, cy = rw // 2, rh // 2

    sx = max(0, cx - new_w // 2)
    sy = max(0, cy - new_h // 2)

    cropped = roi[
        sy:sy + new_h,
        sx:sx + new_w
    ]

    zoomed = cv2.resize(
        cropped,
        (rw, rh),
        interpolation=cv2.INTER_LINEAR
    )

    frame[y1:y2, x1:x2] = zoomed

    return frame


# ==========================================
# SHAKE
# ==========================================

def apply_shake(frame, intensity):

    dx = random.randint(-intensity, intensity)
    dy = random.randint(-intensity, intensity)

    matrix = np.float32([
        [1, 0, dx],
        [0, 1, dy]
    ])

    return cv2.warpAffine(
        frame,
        matrix,
        (frame.shape[1], frame.shape[0])
    )


# ==========================================
# FLASH
# ==========================================

def apply_flash(frame, intensity):

    overlay = np.full_like(frame, 255)

    return cv2.addWeighted(
        frame,
        1 - intensity,
        overlay,
        intensity,
        0
    )


# ==========================================
# RGB SPLIT
# ==========================================

def apply_rgb_split(frame, bbox, offset=8):

    x1, y1, x2, y2 = get_effect_bbox(
        frame, bbox
    )

    roi = frame[y1:y2, x1:x2].copy()

    if roi.size == 0:
        return frame

    blue, green, red = cv2.split(roi)

    red = np.roll(red, offset, axis=1)
    blue = np.roll(blue, -offset, axis=1)

    frame[y1:y2, x1:x2] = cv2.merge([
        blue,
        green,
        red
    ])

    return frame


# ==========================================
# COLOR GRADING
# ==========================================

def apply_color_grade(frame):

    graded = cv2.convertScaleAbs(
        frame,
        alpha=1.18,
        beta=5
    )

    hsv = cv2.cvtColor(
        graded,
        cv2.COLOR_BGR2HSV
    )

    hsv[:, :, 1] = np.clip(
        hsv[:, :, 1].astype(np.float32) * 1.25,
        0,
        255
    ).astype(np.uint8)

    return cv2.cvtColor(
        hsv,
        cv2.COLOR_HSV2BGR
    )


# ==========================================
# TEMPLATE EFFECT ENGINE
# ==========================================

def apply_template(frame, bbox, elapsed, template):

    bpm = template["bpm"]

    beat_interval = 60.0 / bpm

    beat_phase = elapsed % beat_interval

    # Beat detection based on configured BPM
    beat = beat_phase < 0.14

    # Animated zoom
    zoom = 0.10 + 0.12 * (
        0.5 + 0.5 * np.sin(
            elapsed * 2 * np.pi * 1.2
        )
    )

    if beat:
        zoom += 0.15

    # Color grading
    frame = apply_color_grade(frame)

    # Zoom
    frame = apply_zoom(
        frame,
        bbox,
        zoom
    )

    # Shake
    if beat and int(elapsed / beat_interval) % 2 == 0:

        frame = apply_shake(
            frame,
            7
        )

    # RGB split
    if beat:

        frame = apply_rgb_split(
            frame,
            bbox,
            offset=8
        )

    # Flash
    if int(elapsed) in [2, 5, 8]:

        if elapsed % 1 < 0.12:

            frame = apply_flash(
                frame,
                0.35
            )

    return frame
