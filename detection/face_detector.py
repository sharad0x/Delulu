
import cv2


# Load Haar Cascades
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades +
    "haarcascade_frontalface_default.xml"
)

profile_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades +
    "haarcascade_profileface.xml"
)


def detect_face(frame):

    gray = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2GRAY
    )

    gray = cv2.equalizeHist(gray)

    # Frontal face detection
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=6,
        minSize=(70, 70)
    )

    # Profile face detection
    if len(faces) == 0:

        profiles = profile_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(70, 70)
        )

        # Detect opposite-facing profiles
        if len(profiles) == 0:

            flipped = cv2.flip(gray, 1)

            profiles = profile_cascade.detectMultiScale(
                flipped,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(70, 70)
            )

            profiles = [
                (gray.shape[1] - x - w, y, w, h)
                for x, y, w, h in profiles
            ]

        faces = profiles

    if len(faces) == 0:
        return None

    # Return largest detected face
    return max(
        faces,
        key=lambda f: f[2] * f[3]
    )
