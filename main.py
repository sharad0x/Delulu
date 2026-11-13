
import cv2
import time
from pathlib import Path

# ==========================================
# MODULE IMPORTS
# ==========================================

from detection.face_detector import detect_face

from detection.face_tracker import (
    initialize_tracker,
    update_tracker
)

from editing.effects import apply_template

from editing.template_manager import (
    get_templates,
    select_random_template
)

from audio.music_player import (
    initialize_audio,
    play_song,
    stop_song,
    shutdown_audio
)


# ==========================================
# PROJECT CONFIGURATION
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parent

CAMERA_ID = 0

CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

EDIT_DURATION = 10
COOLDOWN = 5

WINDOW_NAME = "Aura++"


# ==========================================
# APPLICATION STATES
# ==========================================

DETECTING = "DETECTING"
EDITING = "EDITING"
COOLDOWN_STATE = "COOLDOWN"


# ==========================================
# INITIALIZATION
# ==========================================

def main():

    state = DETECTING

    tracker = None
    face_bbox = None

    active_template = None

    edit_start = 0
    cooldown_start = 0

    # Load available templates
    templates = get_templates(PROJECT_ROOT)

    if not templates:
        raise RuntimeError(
            "No MP3 songs found in assets/songs/"
        )

    print("Available templates:")

    for template in templates:
        print(
            f" - {template['name']} "
            f"({template['bpm']} BPM)"
        )

    # Initialize audio
    initialize_audio()

    # Initialize webcam
    cap = cv2.VideoCapture(CAMERA_ID)

    cap.set(
        cv2.CAP_PROP_FRAME_WIDTH,
        CAMERA_WIDTH
    )

    cap.set(
        cv2.CAP_PROP_FRAME_HEIGHT,
        CAMERA_HEIGHT
    )

    if not cap.isOpened():
        shutdown_audio()
        raise RuntimeError("Cannot access webcam")

    # Fullscreen window
    cv2.namedWindow(
        WINDOW_NAME,
        cv2.WINDOW_NORMAL
    )

    cv2.setWindowProperty(
        WINDOW_NAME,
        cv2.WND_PROP_FULLSCREEN,
        cv2.WINDOW_FULLSCREEN
    )

    print("\nAura++ Live Editing Engine Started!")

    # ======================================
    # MAIN LOOP
    # ======================================

    try:

        while True:

            ret, frame = cap.read()

            if not ret:
                break

            # Mirror camera feed
            frame = cv2.flip(frame, 1)

            current_time = time.monotonic()

            # ==================================
            # STATE 1: FACE DETECTION
            # ==================================

            if state == DETECTING:

                face = detect_face(frame)

                if face is not None:

                    face_bbox = tuple(
                        map(int, face)
                    )

                    # Initialize tracker
                    tracker = initialize_tracker(
                        frame,
                        face_bbox
                    )

                    # Random template selection
                    active_template = select_random_template(
                        templates
                    )

                    print(
                        "\nSelected template:",
                        active_template["name"]
                    )

                    # Start music
                    play_song(
                        active_template["song"]
                    )

                    edit_start = time.monotonic()

                    state = EDITING

                    print("Live editing started.")

            # ==================================
            # STATE 2: LIVE EDITING
            # ==================================

            elif state == EDITING:

                elapsed = current_time - edit_start

                # Update face tracking
                updated_bbox = update_tracker(
                    tracker,
                    frame
                )

                if updated_bbox is not None:

                    face_bbox = updated_bbox

                # Apply editing effects
                if face_bbox is not None:

                    frame = apply_template(
                        frame,
                        face_bbox,
                        elapsed,
                        active_template
                    )

                # Finish editing
                duration = active_template["duration"]

                if elapsed >= duration:

                    stop_song()

                    cooldown_start = current_time

                    state = COOLDOWN_STATE

                    print(
                        "Editing completed. "
                        "Cooldown started."
                    )

            # ==================================
            # STATE 3: COOLDOWN
            # ==================================

            elif state == COOLDOWN_STATE:

                cooldown_elapsed = (
                    current_time - cooldown_start
                )

                if cooldown_elapsed >= COOLDOWN:

                    # Reset editing variables
                    tracker = None
                    face_bbox = None
                    active_template = None

                    state = DETECTING

                    print(
                        "Cooldown completed. "
                        "Detecting again."
                    )

            # ==================================
            # DISPLAY
            # ==================================

            cv2.imshow(
                WINDOW_NAME,
                frame
            )

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:

        # Cleanup
        stop_song()

        shutdown_audio()

        cap.release()

        cv2.destroyAllWindows()

        print("\nAura++ stopped.")


# ==========================================
# ENTRY POINT
# ==========================================

if __name__ == "__main__":
    main()
