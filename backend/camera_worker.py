import cv2
import threading
import sys
import os
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage
from ultralytics import YOLO
from datetime import datetime
import geocoder

from utils.email_alert import send_email
from utils.logger import log_pothole_event


# ===============================
# 🔑 EXE SAFE PATH HELPER
# ===============================
def resource_path(relative_path):
    """
    Get absolute path to resource (works for dev & PyInstaller exe)
    """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class CameraThread(QThread):
    # image, severity, confidence(%), last_time
    frameReady = Signal(QImage, str, float, str)

    def __init__(self):
        super().__init__()
        self.running = False

        # ✅ FIXED MODEL PATH FOR EXE
        model_path = resource_path(
            "runs/detect/train8/weights/best.pt"
        )
        self.model = YOLO(model_path)

        self.email_sent = False

    def run(self):
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cap.isOpened():
            return

        self.running = True
        self.email_sent = False

        while self.running:
            ret, frame = cap.read()
            if not ret:
                continue

            h, w, _ = frame.shape
            frame_area = h * w

            results = self.model(frame, conf=0.60, device=0)

            severity = "None"
            max_conf = 0.0
            last_time = "--"
            pothole_detected = False
            count = len(results[0].boxes)

            for box in results[0].boxes:
                pothole_detected = True

                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                max_conf = max(max_conf, conf)

                area_ratio = ((x2 - x1) * (y2 - y1)) / frame_area
                if area_ratio < 0.02:
                    severity = "Small"
                    color = (0, 255, 0)
                elif area_ratio < 0.06:
                    severity = "Medium"
                    color = (0, 255, 255)
                else:
                    severity = "Large"
                    color = (0, 0, 255)

                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(
                    frame,
                    f"{severity} {conf:.2f}",
                    (x1, y1 - 8),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    color,
                    2
                )

            if pothole_detected:
                last_time = datetime.now().strftime("%H:%M:%S")

            # 🔔 EMAIL + CSV (ONCE PER EVENT)
            if pothole_detected and not self.email_sent:
                self.email_sent = True
                threading.Thread(
                    target=self.handle_alert,
                    args=(frame.copy(), severity, count),
                    daemon=True
                ).start()

            if not pothole_detected:
                self.email_sent = False
                severity = "None"
                max_conf = 0.0

            confidence_percent = round(max_conf * 100, 1)

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = QImage(
                frame.data,
                w,
                h,
                3 * w,
                QImage.Format_RGB888
            ).copy()

            self.frameReady.emit(
                img,
                severity,
                confidence_percent,
                last_time
            )

        cap.release()

    def stop(self):
        self.running = False
        self.wait()

    def handle_alert(self, frame, severity, count):
        now = datetime.now()
        date = now.strftime("%Y-%m-%d")
        time = now.strftime("%H-%M-%S")

        g = geocoder.ip("me")
        lat, lng = ("N/A", "N/A")
        if g.ok and g.latlng:
            lat, lng = g.latlng

        # ✅ FIXED SAVE PATHS FOR EXE
        image_dir = resource_path("alerts/images")
        log_dir = resource_path("alerts/logs")

        os.makedirs(image_dir, exist_ok=True)
        os.makedirs(log_dir, exist_ok=True)

        image_path = os.path.join(
            image_dir,
            f"pothole_{date}_{time}.jpg"
        )

        cv2.imwrite(image_path, frame)

        log_pothole_event(
            date,
            time,
            "Mysore",
            lat,
            lng,
            severity,
            count
        )

        send_email(
            image_path=image_path,
            csv_path=os.path.join(log_dir, "pothole_log.csv"),
            date=date,
            time=time,
            location=f"Mysore\nLat: {lat}, Lng: {lng}",
            severity=severity
        )

