import sys
import os

# ==============================
# SETUP PATH AGAR FOLDER TERBACA
# ==============================
# Mengambil direktori file main.py saat ini
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Menambahkan BASE_DIR ke sys.path agar folder widgets & styles bisa di-import
sys.path.insert(0, BASE_DIR)

# ==============================
# IMPORT LIBRARY & WIDGET
# ==============================
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMessageBox

# Import style aplikasi
from styles import APP_STYLE

# Import semua halaman / widget aplikasi
from widgets.login_widget import LoginWidget
from widgets.index_widget import IndexWidget
from widgets.add_item_widget import AddItemWidget
from widgets.scan_widget import ScanWidget
from widgets.view_item_widget import ViewItemWidget
from widgets.edit_item_widget import EditItemWidget
from widgets.user_widget import UserWidget


class MainWindow(QMainWindow):
    """
    MainWindow adalah window utama aplikasi.
    Mengatur navigasi antar halaman menggunakan QStackedWidget.
    """

    def __init__(self):
        super().__init__()

        # Judul dan ukuran window
        self.setWindowTitle("Industrial Stock System - Desktop")
        self.resize(1200, 800)

        # ==============================
        # VARIABEL SESI USER (LOGIN)
        # ==============================
        self.current_user_fullname = ""  # Menyimpan nama lengkap user login
        self.current_user_role = ""  # Menyimpan role user (admin/user)

        # ==============================
        # ROOT STACK (LOGIN vs APP)
        # ==============================
        # Stack utama untuk berpindah antara login dan konten aplikasi
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # ==============================
        # HALAMAN LOGIN
        # ==============================
        self.login_page = LoginWidget()

        # Signal login sukses dari LoginWidget
        self.login_page.logged_in.connect(self.on_login_success)

        # ==============================
        # HALAMAN KONTEN UTAMA (SUB-STACK)
        # ==============================
        self.content = QStackedWidget()

        # Inisialisasi halaman utama
        self.dashboard = IndexWidget()
        self.add_item = AddItemWidget()
        self.scan = ScanWidget()
        self.user_page = UserWidget()

        # Menambahkan widget ke sub-stack
        self.content.addWidget(self.dashboard)  # Index 0
        self.content.addWidget(self.add_item)  # Index 1
        self.content.addWidget(self.scan)  # Index 2
        self.content.addWidget(self.user_page)  # Index 3

        # ==============================
        # MASUKKAN KE STACK UTAMA
        # ==============================
        self.stack.addWidget(self.login_page)  # Index 0
        self.stack.addWidget(self.content)  # Index 1

        # Tampilkan halaman login pertama kali
        self.stack.setCurrentIndex(0)

        # Setup semua koneksi signal & slot
        self.setup_connections()

    def setup_connections(self):
        """
        Menghubungkan semua tombol dan signal antar widget
        untuk navigasi aplikasi.
        """

        # ==============================
        # DASHBOARD SIGNALS
        # ==============================
        self.dashboard.btn_add.clicked.connect(self.show_add_item)
        self.dashboard.btn_scan.clicked.connect(self.show_scan)

        # Tombol logout
        self.dashboard.btn_logout.clicked.connect(self.handle_logout)

        # Tombol manage users (jika ada)
        if hasattr(self.dashboard, 'btn_manage_users'):
            self.dashboard.btn_manage_users.clicked.connect(self.show_manage_users)

        # Signal view dan edit item dari dashboard
        self.dashboard.view_item.connect(self.open_view)
        self.dashboard.edit_item.connect(self.open_edit)

        # ==============================
        # ADD ITEM SIGNALS
        # ==============================
        self.add_item.item_added.connect(self.show_dashboard)
        self.add_item.cancelled.connect(self.show_dashboard)

        # ==============================
        # SCAN SIGNALS
        # ==============================
        self.scan.back_to_dashboard.connect(self.show_dashboard)
        self.scan.item_found.connect(self.open_view)

        # ==============================
        # USER MANAGEMENT SIGNAL
        # ==============================
        self.user_page.back_to_dashboard.connect(self.show_dashboard)

    # =========================
    # LOGIKA LOGIN & LOGOUT
    # =========================

    def on_login_success(self, username, fullname, role):
        """
        Dipanggil saat login berhasil.
        Menerima data user dari LoginWidget.
        """
        self.current_user_fullname = fullname
        self.current_user_role = role

        # Kirim data user ke dashboard
        self.dashboard.set_user_data(fullname, role)

        # Pindah dari login ke konten aplikasi
        self.stack.setCurrentIndex(1)
        self.show_dashboard()

    def handle_logout(self):
        """
        Menangani proses logout user.
        """
        confirm = QMessageBox.question(
            self,
            "Logout",
            "Apakah Anda yakin ingin keluar?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            # Reset sesi user
            self.current_user_fullname = ""
            self.current_user_role = ""

            # Kembali ke halaman login
            self.stack.setCurrentIndex(0)

    # =========================
    # NAVIGASI HALAMAN
    # =========================

    def show_dashboard(self):
        """
        Menampilkan dashboard dan refresh data tabel.
        """
        self.dashboard.refresh_list()
        self.content.setCurrentWidget(self.dashboard)
        self.clear_temporary_widgets()

    def show_add_item(self):
        """Menampilkan halaman tambah item"""
        self.content.setCurrentWidget(self.add_item)

    def show_scan(self):
        """Menampilkan halaman scan barcode"""
        self.content.setCurrentWidget(self.scan)

    def show_manage_users(self):
        """Menampilkan halaman manajemen user"""
        self.user_page.refresh_users()
        self.content.setCurrentWidget(self.user_page)

    def clear_temporary_widgets(self):
        """
        Menghapus widget dinamis (View/Edit)
        agar tidak terjadi memory leak.
        """
        while self.content.count() > 4:
            widget = self.content.widget(4)
            self.content.removeWidget(widget)
            widget.deleteLater()

    # =========================
    # VIEW & EDIT ITEM (DINAMIS)
    # =========================

    def open_view(self, item_id: int):
        """
        Membuka halaman detail item (View).
        """
        self.clear_temporary_widgets()

        view_page = ViewItemWidget(item_id)
        view_page.back_to_dashboard.connect(self.show_dashboard)
        view_page.go_to_edit.connect(self.open_edit)

        self.content.addWidget(view_page)
        self.content.setCurrentWidget(view_page)

    def open_edit(self, item_id: int):
        """
        Membuka halaman edit item.
        Nama user login dikirim untuk dicatat
        sebagai pengubah data.
        """
        self.clear_temporary_widgets()

        edit_page = EditItemWidget(item_id, self.current_user_fullname)

        edit_page.btn_save.clicked.connect(self.show_dashboard)
        edit_page.btn_cancel.clicked.connect(self.show_dashboard)

        self.content.addWidget(edit_page)
        self.content.setCurrentWidget(edit_page)


# =========================
# ENTRY POINT APLIKASI
# =========================
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Terapkan style aplikasi jika tersedia
    if 'APP_STYLE' in globals():
        app.setStyleSheet(APP_STYLE)

    window = MainWindow()
    window.show()

    # Menjalankan event loop aplikasi
    sys.exit(app.exec())
