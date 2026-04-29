import os
import bcrypt
from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QFrame, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap

# Modul koneksi database
from db import get_conn
# Modul Auth jika diperlukan untuk session management
from auth import Auth

class LoginWidget(QWidget):
    # Sinyal diperbarui untuk mengirim (username, fullname, role)
    # Ini penting agar Dashboard bisa menampilkan nama user dan membatasi akses hapus
    logged_in = Signal(str, str, str) 

    def __init__(self):
        super().__init__()
        self.setMinimumSize(800, 600)
        self.setup_ui()

    def setup_ui(self):
        # BACKGROUND IMAGE
        base_dir = os.path.dirname(os.path.dirname(__file__))
        bg_path = os.path.join(base_dir, "assets", "bg_login.jpg")

        self.bg = QLabel(self)
        if os.path.exists(bg_path):
            self.bg.setPixmap(QPixmap(bg_path))
        self.bg.setScaledContents(True)
        self.bg.lower()

        self.card = QFrame(self)
        self.card.setFixedSize(420, 320)
        self.card.setObjectName("loginCard")
        self.card.setStyleSheet("""
            QFrame#loginCard {
                background-color: rgba(255, 255, 255, 0.85);
                border-radius: 22px;
                border: 1px solid rgba(255, 255, 255, 0.3);
            }
        """)

        layout = QVBoxLayout(self.card)
        layout.setContentsMargins(35, 30, 35, 30)
        layout.setSpacing(15)

        title = QLabel("User Login")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 26px; font-weight: 700; color: #0d6efd;")
        layout.addWidget(title)
        layout.addSpacing(25)

        # USERNAME INPUT
        self.input_username = QLineEdit()
        self.input_username.setPlaceholderText("Username") 
        self.input_username.setFixedHeight(40)
        self.input_username.setStyleSheet(self.input_style())
        layout.addWidget(self.input_username)

        # PASSWORD INPUT
        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("Password") 
        self.input_password.setEchoMode(QLineEdit.Password)
        self.input_password.setFixedHeight(40)
        self.input_password.setStyleSheet(self.input_style())
        layout.addWidget(self.input_password)

        # BUTTON SIGN IN
        self.btn_login = QPushButton("Sign in")
        self.btn_login.setFixedHeight(44)
        self.btn_login.setStyleSheet("""
            QPushButton {
                background: #0d6efd;
                color: white;
                border-radius: 22px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #0b5ed7;
            }
        """)
        self.btn_login.clicked.connect(self.do_login)

        layout.addSpacing(20)
        layout.addWidget(self.btn_login)
        layout.addStretch(1)

        self.update_layout()

    def input_style(self):
        return """
            QLineEdit {
                background: rgba(255,255,255,0.9);
                border: 1px solid #ccc; 
                border-radius: 20px;
                padding-left: 15px;
                font-size: 15px;
                color: black; 
            }
            QLineEdit::placeholder {
                color: #888; 
            }
            QLineEdit:focus {
                border: 2px solid #0d6efd;
            }
        """

    def resizeEvent(self, event):
        self.update_layout()

    def update_layout(self):
        w, h = self.width(), self.height()
        self.bg.setGeometry(0, 0, w, h)
        self.card.move(
            (w - self.card.width()) // 2,
            (h - self.card.height()) // 2
        )

    def do_login(self):
        username = self.input_username.text().strip()
        password_input = self.input_password.text().strip()

        if not username or not password_input:
            QMessageBox.warning(self, "Peringatan", "Username dan password wajib diisi.")
            return

        conn = None
        try:
            conn = get_conn()
            with conn.cursor() as cur:
                # Mengambil username, password (hash), fullname, dan role
                sql = "SELECT username, password, fullname, role FROM users WHERE username=%s"
                cur.execute(sql, (username,)) 
                row = cur.fetchone()

            if row is None:
                QMessageBox.warning(self, "Gagal Login", "Username tidak ditemukan.")
                return

            # Proses validasi password menggunakan bcrypt
            db_password_hash = row["password"].encode('utf-8')
            if not bcrypt.checkpw(password_input.encode('utf-8'), db_password_hash):
                QMessageBox.warning(self, "Gagal Login", "Password salah.")
                return

            # Set session di Auth module
            Auth.login(row)
            
            # Memancarkan sinyal ke main.py dengan data lengkap
            # row['fullname'] digunakan untuk menyapa di Dashboard
            # row['role'] digunakan untuk proteksi tombol hapus
            self.logged_in.emit(row['username'], row['fullname'], row['role'])

        except Exception as e:
            # Menangani error seperti "Invalid salt" jika password di DB bukan bcrypt hash
            QMessageBox.critical(self, "Koneksi/Error Database", f"Terjadi kesalahan saat login: {str(e)}")
        finally:
            if conn:
                conn.close()