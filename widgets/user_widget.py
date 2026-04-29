import os
import bcrypt  # Library untuk enkripsi password
from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, 
    QHBoxLayout, QFrame, QTableWidget, QTableWidgetItem, 
    QHeaderView, QComboBox, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from db import get_conn

class UserWidget(QWidget):
    back_to_dashboard = Signal()

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.refresh_users()

    def setup_ui(self):
        base_dir = os.path.dirname(os.path.dirname(__file__))
        bg_path = os.path.join(base_dir, "assets", "bg_dashboard.jpg")
        
        self.bg = QLabel(self)
        if os.path.exists(bg_path):
            self.bg.setPixmap(QPixmap(bg_path))
        self.bg.setScaledContents(True)
        self.bg.lower()

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(50, 50, 50, 50)

        # Efek Transparan (Frosted Glass)
        self.card = QFrame()
        self.card.setObjectName("UserCard")
        self.card.setStyleSheet("""
            QFrame#UserCard {
                background-color: rgba(255, 255, 255, 0.85);
                border-radius: 40px;
                border: 1px solid rgba(255, 255, 255, 0.3);
            }
        """)
        root_layout.addWidget(self.card)

        layout = QVBoxLayout(self.card)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(15)

        # Header Section
        header = QHBoxLayout()
        title_v = QVBoxLayout()
        title = QLabel("Manage Users")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #1a1a1a; background: transparent;")
        subtitle = QLabel("Tambah / kelola akun pengguna sistem")
        subtitle.setStyleSheet("font-size: 14px; color: #666; background: transparent;")
        title_v.addWidget(title)
        title_v.addWidget(subtitle)
        header.addLayout(title_v)

        self.btn_back = QPushButton("Back")
        self.btn_back.setFixedSize(80, 35)
        self.btn_back.setStyleSheet("background-color: #6c757d; color: white; border-radius: 8px; font-weight: bold;")
        self.btn_back.clicked.connect(lambda: self.back_to_dashboard.emit())
        header.addStretch()
        header.addWidget(self.btn_back)
        layout.addLayout(header)

        # Form Inputs
        self.input_user = QLineEdit(); self.input_user.setPlaceholderText("Username")
        self.input_fullname = QLineEdit(); self.input_fullname.setPlaceholderText("Full Name")
        self.input_pass = QLineEdit(); self.input_pass.setPlaceholderText("Password Baru")
        self.input_pass.setEchoMode(QLineEdit.Password)
        
        self.combo_role = QComboBox()
        self.combo_role.addItems(["Admin", "Operator"])

        # Style Dropdown & Input
        input_style = """
            QLineEdit, QComboBox { 
                background-color: white; 
                border-radius: 10px; 
                padding: 12px; 
                border: 1px solid #ddd; 
                color: black; 
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: black;
                selection-background-color: #0d6efd;
                selection-color: white;
            }
        """
        for w in [self.input_user, self.input_fullname, self.input_pass, self.combo_role]:
            w.setStyleSheet(input_style)
            layout.addWidget(w)

        self.btn_save = QPushButton("Tambah User")
        self.btn_save.setFixedHeight(50)
        self.btn_save.setStyleSheet("background-color: #0d6efd; color: white; border-radius: 12px; font-weight: bold; font-size: 16px;")
        self.btn_save.clicked.connect(self.add_user)
        layout.addWidget(self.btn_save)

        # Table Section
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Username", "Full Name", "Role"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet("""
            QTableWidget { background-color: white; border-radius: 15px; color: black; }
            QHeaderView::section { background-color: #f8f9fa; font-weight: bold; color: black; border: none; padding: 10px; }
        """)
        layout.addWidget(self.table)

    def refresh_users(self):
        """Memuat daftar pengguna dari database"""
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT username, fullname, role FROM users ORDER BY username ASC")
                rows = cur.fetchall()
                
                self.table.setRowCount(len(rows))
                for idx, row in enumerate(rows):
                    self.table.setItem(idx, 0, QTableWidgetItem(str(row.get('username', '-'))))
                    self.table.setItem(idx, 1, QTableWidgetItem(str(row.get('fullname', '-'))))
                    self.table.setItem(idx, 2, QTableWidgetItem(str(row.get('role', '-'))))
        except Exception as e:
            print(f"Error Refresh Table: {e}")
        finally:
            conn.close()

    def add_user(self):
        """Menyimpan user baru dengan password yang sudah di-hash"""
        user = self.input_user.text().strip()
        full = self.input_fullname.text().strip()
        pwd = self.input_pass.text().strip()
        role = self.combo_role.currentText().lower()

        if not user or not pwd or not full:
            QMessageBox.warning(self, "Peringatan", "Semua kolom wajib diisi!")
            return

        # --- PROSES ENKRIPSI (HASHING) ---
        # Generate salt dan hash password
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(pwd.encode('utf-8'), salt)

        conn = get_conn()
        try:
            with conn.cursor() as cur:
                # Simpan hashed_password ke database (dalam bentuk string didecode)
                sql = "INSERT INTO users (username, fullname, password, role) VALUES (%s, %s, %s, %s)"
                cur.execute(sql, (user, full, hashed_password.decode('utf-8'), role))
                
                conn.commit()
                QMessageBox.information(self, "Sukses", "User berhasil ditambahkan dengan password terenkripsi!")
                
                # Bersihkan form dan refresh tabel
                self.input_user.clear()
                self.input_fullname.clear()
                self.input_pass.clear()
                self.refresh_users()
                
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Gagal simpan: {e}")
        finally:
            conn.close()

    def resizeEvent(self, event):
        if hasattr(self, 'bg'): self.bg.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)