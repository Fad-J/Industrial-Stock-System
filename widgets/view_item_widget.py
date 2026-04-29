import os
import qrcode
from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, 
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QDialog
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QImage
from db import get_conn

class ViewItemWidget(QWidget):
    back_to_dashboard = Signal()
    go_to_edit = Signal(int)

    def __init__(self, item_id=None):
        super().__init__()
        self.item_id = item_id
        self.current_sku = "" 
        self.setup_ui()
        
        if self.item_id:
            self.load_item_details(self.item_id)
            self.load_history(self.item_id)

    def setup_ui(self):
        base_dir = os.path.dirname(os.path.dirname(__file__))
        bg_path = os.path.join(base_dir, "assets", "bg_dashboard.jpg")
        self.bg = QLabel(self)
        if os.path.exists(bg_path): self.bg.setPixmap(QPixmap(bg_path))
        self.bg.setScaledContents(True)
        self.bg.lower()

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(40, 40, 40, 40)
        self.main_layout.setSpacing(25)

        # DETAIL CARD
        self.detail_card = QFrame()
        self.detail_card.setObjectName("DetailCard")
        self.detail_card.setStyleSheet("QFrame#DetailCard { background-color: #ffffff; border-radius: 20px; border: 1px solid #ddd; } QLabel { background: transparent; color: #1a1a1a; }")
        
        detail_layout = QVBoxLayout(self.detail_card)
        detail_layout.setContentsMargins(30, 30, 30, 30)

        header_row = QHBoxLayout()
        self.lbl_title = QLabel("Detail Barang"); self.lbl_title.setStyleSheet("font-size: 32px; font-weight: bold; color: #000;"); header_row.addWidget(self.lbl_title)
        header_row.addStretch()

        self.btn_back = QPushButton("Back"); self.btn_back.setFixedSize(70, 35); self.btn_back.setStyleSheet("background-color: #6c757d; color: white; border-radius: 8px; font-weight: bold;"); self.btn_back.clicked.connect(lambda: self.back_to_dashboard.emit()); header_row.addWidget(self.btn_back)
        self.btn_edit = QPushButton("Edit"); self.btn_edit.setFixedSize(70, 35); self.btn_edit.setStyleSheet("background-color: #0d6efd; color: white; border-radius: 8px; font-weight: bold;"); self.btn_edit.clicked.connect(lambda: self.go_to_edit.emit(self.item_id)); header_row.addWidget(self.btn_edit)
        self.btn_qr = QPushButton("QR"); self.btn_qr.setFixedSize(50, 35); self.btn_qr.setStyleSheet("background-color: #212529; color: white; border-radius: 8px; font-weight: bold;"); self.btn_qr.clicked.connect(self.generate_qr_dialog); header_row.addWidget(self.btn_qr)
        detail_layout.addLayout(header_row)

        info_row = QHBoxLayout()
        self.block_sku = self.create_info_block("SKU"); self.block_barcode = self.create_info_block("Barcode"); self.block_lokasi = self.create_info_block("Lokasi"); self.block_qty = self.create_info_block("Qty"); self.block_harga = self.create_info_block("Harga / item")
        info_row.addLayout(self.block_sku); info_row.addLayout(self.block_barcode); info_row.addLayout(self.block_lokasi); info_row.addLayout(self.block_qty); info_row.addLayout(self.block_harga); detail_layout.addLayout(info_row)
        self.main_layout.addWidget(self.detail_card)

        # HISTORY BOX
        self.history_container = QFrame()
        self.history_container.setStyleSheet("background-color: #ffffff; border-radius: 15px; border: 1px solid #ccc;")
        h_box_layout = QVBoxLayout(self.history_container)
        h_box_layout.setContentsMargins(20, 20, 20, 20)
        
        history_title = QLabel("History Pergerakan Stok")
        history_title.setStyleSheet("font-size: 22px; font-weight: bold; color: #000; border:none;")
        h_box_layout.addWidget(history_title)

        self.table_history = QTableWidget(0, 4)
        self.table_history.setHorizontalHeaderLabels(["Waktu", "Perubahan", "User ID", "Keterangan"])
        self.table_history.setEditTriggers(QTableWidget.NoEditTriggers) 
        
        # --- PERBAIKAN: AGAR TEKS TIDAK TERPOTONG ---
        self.table_history.setWordWrap(True) # Aktifkan bungkus teks otomatis
        self.table_history.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents) # Baris memanjang ke bawah
        
        header = self.table_history.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed); self.table_history.setColumnWidth(0, 150)
        header.setSectionResizeMode(1, QHeaderView.Fixed); self.table_history.setColumnWidth(1, 100)
        header.setSectionResizeMode(2, QHeaderView.Stretch) # User ID lebar otomatis
        header.setSectionResizeMode(3, QHeaderView.Stretch) # Keterangan lebar otomatis
        
        self.table_history.verticalHeader().setVisible(False)
        self.table_history.setStyleSheet("QTableWidget { border: none; font-size: 14px; color: #000; background-color: #fff; }")
        h_box_layout.addWidget(self.table_history)
        self.main_layout.addWidget(self.history_container)

    def create_info_block(self, title):
        layout = QVBoxLayout(); lbl_t = QLabel(title); lbl_t.setStyleSheet("font-weight: bold; font-size: 14px; color: #666;"); lbl_v = QLabel("-"); lbl_v.setStyleSheet("font-size: 18px; color: #0d6efd; font-weight: bold;"); layout.addWidget(lbl_t); layout.addWidget(lbl_v); layout.value_label = lbl_v; return layout

    def load_item_details(self, item_id):
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM items WHERE id = %s", (item_id,))
                item = cur.fetchone()
                if item:
                    self.current_sku = str(item.get('sku', '')) 
                    self.block_sku.value_label.setText(self.current_sku)
                    self.block_barcode.value_label.setText(str(item.get('barcode', '-')))
                    self.block_lokasi.value_label.setText(str(item.get('location', '-')))
                    self.block_qty.value_label.setText(str(item.get('qty', '0')))
                    self.block_harga.value_label.setText(f"Rp {float(item.get('price', 0)):,.0f}")
        finally:
            conn.close()

    def load_history(self, item_id):
        """Memuat riwayat dengan data User ID yang benar"""
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                sql = "SELECT created_at, change_amount, user_id_name, reason FROM stock_movements WHERE item_id = %s ORDER BY created_at DESC"
                cur.execute(sql, (item_id,))
                rows = cur.fetchall()
                self.table_history.setRowCount(len(rows))
                for idx, row in enumerate(rows):
                    self.table_history.setItem(idx, 0, QTableWidgetItem(str(row['created_at'])))
                    self.table_history.setItem(idx, 1, QTableWidgetItem(str(row['change_amount'] or "0")))
                    # FIX: Menampilkan nama pengubah asli
                    self.table_history.setItem(idx, 2, QTableWidgetItem(str(row['user_id_name'] or "Unknown")))
                    self.table_history.setItem(idx, 3, QTableWidgetItem(str(row['reason'] or "-")))
        finally:
            conn.close()

    def generate_qr_dialog(self):
        if not self.current_sku: return
        qr = qrcode.QRCode(version=1, box_size=10, border=5); qr.add_data(self.current_sku); qr.make(fit=True); img = qr.make_image(fill_color="black", back_color="white").convert("RGBA"); qim = QImage(img.tobytes("raw", "RGBA"), img.size[0], img.size[1], QImage.Format_RGBA8888); dialog = QDialog(self); d_layout = QVBoxLayout(dialog); qr_lbl = QLabel(); qr_lbl.setPixmap(QPixmap.fromImage(qim).scaled(300, 300, Qt.KeepAspectRatio)); d_layout.addWidget(qr_lbl); dialog.exec()

    def resizeEvent(self, event):
        if hasattr(self, 'bg'): self.bg.setGeometry(0, 0, self.width(), self.height())