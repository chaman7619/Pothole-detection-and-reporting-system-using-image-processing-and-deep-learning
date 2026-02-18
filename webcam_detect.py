from utils.logger import log_pothole_event
from utils.email_alert import send_email

import cv2
import os
import threading
from datetime import datetime
import geocoder
from ultralytics import YOLO

# ===============================
# LOAD TRAINED YOLO MODEL
# ===============================
model = YOLO("runs/detect/train8/weights/best.pt")

# ===============================
# DIRECTORIES
# ===============================
IMAGE_DIR = "alerts/images"
LOG_DIR = "alerts/logs"
CSV_PATH = os.path.join(LOG_DIR, "pothole_log.csv")

os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# ===============================
# GET LOCATION (FORCED MYSORE)
# ===============================
def get_location():
    g = geocoder.ip("me")

    lat, lng = ("N/A", "N/A")
    if g.ok and g.latlng:
        lat, lng = g.latlng

    location_text = "Mysore, Karnataka, India"
    return location_text, lat, lng


# ===============================
# BACKGROUND TASK (NO FREEZE)
# ===============================
def save_log_and_email(frame, severity, pothole_count):
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H-%M-%S")

    image_path = os.path.join(
        IMAGE_DIR, f"pothole_{date}_{time}.jpg"
    )
    cv2.imwrite(image_path, frame)

    location_text, lat, lng = get_location()

    # CSV LOG
    log_pothole_event(
        date=date,
        time=time,
        city="Mysore",
        latitude=lat,
        longitude=lng,
        severity=severity,
        count=pothole_count
    )

    # EMAIL (IMAGE + CSV)
    send_email(
        image_path=image_path,
        csv_path=CSV_PATH,
        date=date,
        time=time,
        location=f"{location_text}\nLatitude: {lat}, Longitude: {lng}",
        severity=severity
    )


# ===============================
# OPEN WEBCAM
# ===============================
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

print("✅ Pothole detection started. Press Q to quit.")

email_sent_recently = False

# ===============================
# MAIN LOOP
# ===============================
while True:
    ret, frame = cap.read()
    if not ret:
        break

    h, w, _ = frame.shape
    frame_area = h * w

    results = model(
        frame,
        conf=0.63,   # UNCHANGED
        iou=0.5,
        max_det=30,
        device=0
    )

    pothole_detected = False
    severity = "Unknown"
    pothole_count = len(results[0].boxes)

    for box in results[0].boxes:
        pothole_detected = True

        x1, y1, x2, y2 = map(int, box.xyxy[0])
        conf = float(box.conf[0])

        area_ratio = ((x2 - x1) * (y2 - y1)) / frame_area

        if area_ratio < 0.02:
            color = (0, 255, 0)
            severity = "Small"
        elif area_ratio < 0.06:
            color = (0, 255, 255)
            severity = "Medium"
        else:
            color = (0, 0, 255)
            severity = "Large"

        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(
            frame,
            f"Pothole | {severity} | {conf:.2f}",
            (x1, y1 - 6),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            color,
            2
        )

    # ===============================
    # AUTO SAVE + LOG + EMAIL
    # ===============================
    if pothole_detected and not email_sent_recently:
        email_sent_recently = True

        threading.Thread(
            target=save_log_and_email,
            args=(frame.copy(), severity, pothole_count),
            daemon=True
        ).start()

    if not pothole_detected:
        email_sent_recently = False

    cv2.imshow("Pothole Detection - Real Time", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# ===============================
# CLEAN EXIT
# ===============================
cap.release()
cv2.destroyAllWindows()
print("🛑 Detection stopped safely")
