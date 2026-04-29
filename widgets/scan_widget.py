import os
import cv2
import winsound  # Library bawaan untuk mengeluarkan suara beep di Windows
from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, 
    QVBoxLayout, QHBoxLayout, QFrame, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QPixmap, QImage
from db import get_conn

class ScanWidget(QWidget):
    back_to_dashboard = Signal() # Sinyal kirim ke main.py
    item_found = Signal(int)     # Sinyal kirim ID ke main.py

    def __init__(self):
        super().__init__()
        self.cap = None 
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.setup_ui()

    def setup_ui(self):
        base_dir = os.path.dirname(os.path.dirname(__file__))
        bg_path = os.path.join(base_dir, "assets", "bg_dashboard.jpg")
        
        self.bg = QLabel(self)
        if os.path.exists(bg_path):
            self.bg.setPixmap(QPixmap(bg_path))
        self.bg.setScaledContents(True)
        self.bg.lower()

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(50, 50, 50, 50)
        main_layout.setAlignment(Qt.AlignCenter)

        self.card = QFrame()
        self.card.setStyleSheet("background-color: rgba(255, 255, 255, 0.95); border-radius: 30px;")
        
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(40, 40, 40, 40)

        title = QLabel("Scan Barcode / SKU")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #333;")
        card_layout.addWidget(title)

        # TOMBOL KEMBALI
        self.btn_back = QPushButton("← Kembali ke Dashboard")
        self.btn_back.setFixedSize(220, 45)
        self.btn_back.setCursor(Qt.PointingHandCursor)
        self.btn_back.setStyleSheet("""
            QPushButton {
                background-color: #6c757d; color: white; 
                border-radius: 10px; font-weight: bold; font-size: 14px;
            }
            QPushButton:hover { background-color: #5a6268; }
        """)
        self.btn_back.clicked.connect(self.force_exit)
        card_layout.addWidget(self.btn_back)

        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 20, 0, 0)

        # Viewport Kamera
        self.camera_view = QLabel()
        self.camera_view.setFixedSize(500, 350)
        self.camera_view.setText("Kamera Nonaktif")
        self.camera_view.setAlignment(Qt.AlignCenter)
        self.camera_view.setStyleSheet("background-color: black; border-radius: 15px; color: white;")
        content_layout.addWidget(self.camera_view)

        # Kontrol Samping
        controls = QVBoxLayout()
        self.btn_toggle = QPushButton("Nyalakan Kamera")
        self.btn_toggle.setFixedHeight(50)
        self.btn_toggle.setStyleSheet("background-color: #198754; color: white; border-radius: 12px; font-weight: bold;")
        self.btn_toggle.clicked.connect(self.toggle_camera)
        controls.addWidget(self.btn_toggle)

        controls.addSpacing(20)
        self.input_code = QLineEdit()
        self.input_code.setPlaceholderText("Atau ketik SKU manual...")
        self.input_code.setFixedHeight(45)
        self.input_code.setStyleSheet("background: white; border: 1px solid #ccc; border-radius: 10px; padding: 10px;")
        controls.addWidget(self.input_code)

        btn_cek = QPushButton("Cek Manual")
        btn_cek.setFixedHeight(45)
        btn_cek.setStyleSheet("background-color: #0d6efd; color: white; border-radius: 10px; font-weight: bold;")
        btn_cek.clicked.connect(lambda: self.search_item(self.input_code.text()))
        controls.addWidget(btn_cek)

        controls.addStretch()
        content_layout.addLayout(controls)
        card_layout.addLayout(content_layout)
        main_layout.addWidget(self.card)

    def toggle_camera(self):
        if self.cap is None:
            self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) # CAP_DSHOW agar cepat nyala di Windows
            self.timer.start(30)
            self.btn_toggle.setText("Matikan Kamera")
            self.btn_toggle.setStyleSheet("background-color: #dc3545; color: white; border-radius: 12px; font-weight: bold;")
        else:
            self.stop_hardware()

    def stop_hardware(self):
        self.timer.stop()
        if self.cap:
            self.cap.release()
            self.cap = None
        self.camera_view.clear()
        self.camera_view.setText("Kamera Nonaktif")
        self.btn_toggle.setText("Nyalakan Kamera")
        self.btn_toggle.setStyleSheet("background-color: #198754; color: white; border-radius: 12px; font-weight: bold;")

    def update_frame(self):
        if self.cap:
            ret, frame = self.cap.read()
            if ret:
                # Scan QR/Barcode Otomatis
                detector = cv2.QRCodeDetector()
                data, _, _ = detector.detectAndDecode(frame)
                
                if data: 
                    # BUNYI BEEP saat scan berhasil ditemukan
                    winsound.Beep(1000, 250) # Frekuensi 1000Hz, Durasi 250ms
                    self.search_item(data)

                # Tampilkan ke Label
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame.shape
                img = QImage(frame.data, w, h, ch * w, QImage.Format_RGB888)
                self.camera_view.setPixmap(QPixmap.fromImage(img).scaled(500, 350, Qt.KeepAspectRatioByExpanding))

    def force_exit(self):
        """Mematikan hardware dan pindah halaman"""
        self.stop_hardware()
        self.back_to_dashboard.emit()

    def search_item(self, code):
        if not code: return
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM items WHERE sku=%s OR barcode=%s", (code.strip(), code.strip()))
                res = cur.fetchone()
                if res:
                    # BUNYI BEEP saat input manual/scan berhasil dicocokkan ke database
                    if not self.timer.isActive(): winsound.Beep(1000, 250)
                    self.stop_hardware()
                    self.item_found.emit(res['id'])
                else:
                    if not self.timer.isActive(): QMessageBox.warning(self, "Gagal", "SKU tidak ditemukan.")
        finally:
            conn.close()

    def resizeEvent(self, event):
        if hasattr(self, 'bg'):
            self.bg.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)