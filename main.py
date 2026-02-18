import sys, os
from datetime import datetime

from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QFrame,
    QGraphicsDropShadowEffect
)
from PySide6.QtGui import (
    QPixmap, QColor, QFont, QPainter,
    QLinearGradient, QFontDatabase
)
from PySide6.QtCore import Qt

from backend.camera_worker import CameraThread


# ===============================
# 🔑 EXE SAFE PATH HELPER
# ===============================
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # PyInstaller temp folder
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# ===============================
# APPLE FONT
# ===============================
def apple_font(size, weight=QFont.Normal):
    for fam in ["SF Pro Display", "Inter", "Segoe UI Variable", "Segoe UI"]:
        if fam in QFontDatabase().families():
            f = QFont(fam, size)
            f.setWeight(weight)
            return f
    return QFont("Segoe UI", size)


# ===============================
# GLASS CARD
# ===============================
class GlassCard(QFrame):
    def __init__(self, radius=22):
        super().__init__()
        self.radius = radius

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(36)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 100))
        self.setGraphicsEffect(shadow)

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = self.rect().adjusted(0, 0, -1, -1)

        grad = QLinearGradient(0, 0, 0, r.height())
        grad.setColorAt(0.0, QColor(255, 255, 255, 28))
        grad.setColorAt(1.0, QColor(255, 160, 120, 110))

        p.setBrush(grad)
        p.setPen(QColor(255, 255, 255, 35))
        p.drawRoundedRect(r, self.radius, self.radius)
        p.end()


# ===============================
# MAIN WINDOW
# ===============================
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(1366, 820)
        self.setWindowTitle("Pothole Detection System")

        self.cameraThread = None
        self.camera_active = False
        self.last_detected_time = "--"

        # ---------- TITLE ----------
        title = QLabel("Pothole Detection System")
        title.setFont(apple_font(30, QFont.Medium))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color:white; letter-spacing:0.6px;")

        self.statusLabel = QLabel("Status: Idle")
        self.statusLabel.setFont(apple_font(14))
        self.statusLabel.setAlignment(Qt.AlignCenter)
        self.statusLabel.setStyleSheet("color:rgba(255,255,255,0.75);")

        # ---------- CAMERA ----------
        self.cameraLabel = QLabel("Camera is OFF")
        self.cameraLabel.setAlignment(Qt.AlignCenter)
        self.cameraLabel.setFont(apple_font(18))
        self.cameraLabel.setStyleSheet("""
            QLabel {
                background: rgba(45,20,20,0.9);
                color: rgba(255,255,255,0.55);
                border-radius:16px;
            }
        """)
        self.cameraLabel.setFixedSize(720, 420)

        cameraCard = GlassCard()
        camLayout = QVBoxLayout(cameraCard)
        camLayout.setContentsMargins(16,16,16,16)
        camLayout.addWidget(self.cameraLabel)

        # ---------- SUMMARY ----------
        self.summaryStatus = QLabel("Camera: OFF")
        self.summaryStatus.setFont(apple_font(14, QFont.Medium))
        self.summaryStatus.setStyleSheet("color:white;")

        self.severityLbl = QLabel("Severity: None")
        self.confLbl = QLabel("Confidence: --")
        self.timeLbl = QLabel("Last Time: --")

        for lbl in (self.severityLbl, self.confLbl, self.timeLbl):
            lbl.setFont(apple_font(14))
            lbl.setStyleSheet("color:rgba(255,255,255,0.9);")

        summaryCard = GlassCard()
        summaryCard.setFixedSize(280, 420)

        sLayout = QVBoxLayout(summaryCard)
        sLayout.setContentsMargins(24,24,24,24)
        sLayout.setSpacing(22)

        titleSum = QLabel("Detection Summary")
        titleSum.setFont(apple_font(16, QFont.Medium))
        titleSum.setStyleSheet("color:white;")

        sLayout.addWidget(titleSum)
        sLayout.addSpacing(12)
        sLayout.addWidget(self.summaryStatus)
        sLayout.addWidget(self.severityLbl)
        sLayout.addWidget(self.confLbl)
        sLayout.addWidget(self.timeLbl)
        sLayout.addStretch()

        # ---------- CENTER ----------
        center = QHBoxLayout()
        center.setSpacing(20)
        center.setAlignment(Qt.AlignCenter)
        center.addWidget(cameraCard)
        center.addWidget(summaryCard)

        # ---------- CONTROLS ----------
        self.startBtn = QPushButton("Start Camera")
        self.stopBtn = QPushButton("Stop Camera")
        self.logsBtn = QPushButton("Open Logs")

        for b in (self.startBtn, self.stopBtn, self.logsBtn):
            b.setFont(apple_font(14, QFont.Medium))
            b.setFixedSize(160, 44)
            b.setCursor(Qt.PointingHandCursor)
            b.setStyleSheet("""
                QPushButton {
                    background: rgba(235,90,70,1);
                    color:white;
                    border-radius:14px;
                    border:none;
                }
                QPushButton:hover { background: rgba(255,130,90,1); }
                QPushButton:pressed { background: rgba(210,70,60,1); }
            """)

        self.startBtn.clicked.connect(self.start_camera)
        self.stopBtn.clicked.connect(self.stop_camera)
        self.logsBtn.clicked.connect(self.open_logs)

        bottom = GlassCard()
        bLayout = QHBoxLayout(bottom)
        bLayout.setContentsMargins(24,14,24,14)
        bLayout.setSpacing(20)
        bLayout.addWidget(self.startBtn)
        bLayout.addWidget(self.stopBtn)
        bLayout.addWidget(self.logsBtn)

        # ---------- MAIN ----------
        main = QVBoxLayout(self)
        main.setContentsMargins(40,30,40,30)
        main.setSpacing(18)
        main.addWidget(title)
        main.addWidget(self.statusLabel)
        main.addLayout(center)
        main.addWidget(bottom, alignment=Qt.AlignCenter)

    # ---------- BACKGROUND ----------
    def paintEvent(self, e):
        p = QPainter(self)
        g = QLinearGradient(0, 0, 0, self.height())
        g.setColorAt(0.0, QColor(255, 75, 75))
        g.setColorAt(0.5, QColor(255, 120, 80))
        g.setColorAt(1.0, QColor(255, 180, 120))
        p.fillRect(self.rect(), g)
        p.end()

    # ---------- CAMERA ----------
    def start_camera(self):
        if not self.cameraThread:
            self.cameraThread = CameraThread()
            self.cameraThread.frameReady.connect(self.update_frame)
            self.cameraThread.start()
            self.camera_active = True
            self.statusLabel.setText("Status: Camera Active")
            self.summaryStatus.setText("Camera: ON")

    def stop_camera(self):
        if self.cameraThread:
            self.cameraThread.stop()
            self.cameraThread = None
        self.camera_active = False
        self.cameraLabel.setPixmap(QPixmap())
        self.cameraLabel.setText("Camera is OFF")
        self.statusLabel.setText("Status: Idle")
        self.summaryStatus.setText("Camera: OFF")
        self.severityLbl.setText("Severity: None")
        self.confLbl.setText("Confidence: --")
        self.timeLbl.setText("Last Time: --")
        self.last_detected_time = "--"

    # ---------- FRAME UPDATE (FIXED SIGNAL MATCH) ----------
    def update_frame(self, image, severity, confidence, last_time):
        if not self.camera_active:
            return

        pix = QPixmap.fromImage(image).scaled(
            self.cameraLabel.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.cameraLabel.setPixmap(pix)

        self.severityLbl.setText(f"Severity: {severity}")
        self.confLbl.setText(f"Confidence: {confidence:.1f}%")
        self.timeLbl.setText(f"Last Time: {last_time}")

    # ---------- OPEN CSV (EXE SAFE) ----------
    def open_logs(self):
        csv_path = resource_path("alerts/logs/pothole_log.csv")

        if not os.path.exists(csv_path):
            self.statusLabel.setText("Status: Log file not found")
            return

        try:
            os.startfile(csv_path)
            self.statusLabel.setText("Status: Log file opened")
        except Exception:
            self.statusLabel.setText("Status: Failed to open log file")


# ===============================
# RUN
# ===============================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.showFullScreen()
    sys.exit(app.exec())































