APP_STYLE = """
/* =========================
    GLOBAL
    ========================= */
QWidget {
    font-family: "Segoe UI";
    font-size: 14px;
    color: #111111; /* Default text color */
}

/* =========================
    LOGIN CARD
    ========================= */
QFrame#LoginCard {
    background-color: rgba(255, 255, 255, 200);
    border-radius: 25px;
}

/* =========================
    INPUT (LOGIN)
    ========================= */
QFrame#LoginCard QLineEdit {
    background-color: rgba(255,255,255,230);
    border: 1px solid #cccccc;
    border-radius: 20px;
    padding: 10px 15px;
    color: #111111;
    font-size: 15px;
}

QFrame#LoginCard QLineEdit::placeholder {
    color: #777777;
}

/* =========================
    BUTTON (LOGIN)
    ========================= */
QFrame#LoginCard QPushButton {
    background-color: #0d6efd;
    border: none;
    border-radius: 22px;
    padding: 10px;
    color: white;
    font-size: 16px;
    font-weight: bold;
}

QFrame#LoginCard QPushButton:hover {
    background-color: #0b5ed7;
}

QFrame#LoginCard QPushButton:pressed {
    background-color: #0a58ca;
}

/* =========================
    DASHBOARD ROOT
    ========================= */
QWidget#DashboardRoot {
    /* Biarkan default */
}

/* =========================
    DASHBOARD CARD
    ========================= */
QWidget#DashboardCard {
    background-color: white; /* SOLID PUTIH */
    border-radius: 30px;
}

/* =========================
    DASHBOARD WIDGETS
    ========================= */
/* Search Input */
QWidget#DashboardCard QLineEdit {
    background-color: white;
    border: 1px solid #cccccc;
    border-radius: 20px;
    padding: 10px 15px;
    color: #111111;
    font-size: 15px;
}
QWidget#DashboardCard QLineEdit::placeholder {
    color: #777777;
}

/* Action Buttons (General) */
QWidget#DashboardCard QPushButton {
    border-radius: 15px;
    padding: 8px 15px;
    font-weight: 500;
    color: #111111;
}

/* Tombol Tambah Barang (Biru) */
QPushButton#BtnAddItem {
    background-color: #0d6efd;
    color: white;
}
QPushButton#BtnAddItem:hover {
    background-color: #0b5ed7;
}

/* Tombol Scan (Kuning) */
QPushButton#BtnScan {
    background-color: #ffc107;
    color: #111111;
}
QPushButton#BtnScan:hover {
    background-color: #e0a800;
}

/* =========================
    TABLE
    ========================= */
QTableWidget {
    background-color: white;
    border: 1px solid #eeeeee;
    border-radius: 10px;
    gridline-color: #dddddd;
    color: #111111;
}

QHeaderView::section {
    background-color: #f1f3f5;
    padding: 8px;
    border: none;
    font-weight: bold;
    color: #222222;
}

QTableWidget::item {
    padding: 5px;
}
QTableWidget QTableCornerButton::section {
    background: #f1f3f5;
    border: none;
}

/* =========================
   BUTTON AKSI TABLE (View, Edit, Hapus)
   ========================= */
QTableWidget QPushButton {
    border-radius: 8px;
    padding: 4px 6px;
    font-size: 12px;
    font-weight: bold;
    border: none;
}

/* Tombol View (Cyan/Biru Muda) */
QPushButton#BtnView {
    background-color: #17a2b8;
    color: white;
}
QPushButton#BtnView:hover {
    background-color: #138496;
}

/* Tombol Edit (Kuning) */
QPushButton#BtnEdit {
    background-color: #ffc107;
    color: #111111;
}
QPushButton#BtnEdit:hover {
    background-color: #e0a800;
}

/* Tombol Hapus (Merah) */
QPushButton#BtnDelete {
    background-color: #dc3545;
    color: white;
}
QPushButton#BtnDelete:hover {
    background-color: #bd2130;
}

/* Tambahkan di bagian bawah APP_STYLE Anda */

QMessageBox {
    background-color: #2b2b2b;
}

QMessageBox QLabel {
    color: #ffffff; /* Teks notifikasi jadi Putih agar terbaca */
    font-size: 14px;
}

QMessageBox QPushButton {
    background-color: #0d6efd;
    color: white;
    border-radius: 5px;
    padding: 5px 15px;
    min-width: 70px;
}
"""