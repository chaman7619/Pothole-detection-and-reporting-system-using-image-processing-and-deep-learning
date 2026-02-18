import csv
import os

LOG_DIR = "alerts/logs"
LOG_FILE = os.path.join(LOG_DIR, "pothole_log.csv")

os.makedirs(LOG_DIR, exist_ok=True)


def log_pothole_event(date, time, city, latitude, longitude, severity, count):
    file_exists = os.path.isfile(LOG_FILE)

    with open(LOG_FILE, mode="a", newline="") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow([
                "Date",
                "Time",
                "City",
                "Latitude",
                "Longitude",
                "Severity",
                "Pothole_Count"
            ])

        writer.writerow([
            date,
            time,
            city,
            latitude,
            longitude,
            severity,
            count
        ])

