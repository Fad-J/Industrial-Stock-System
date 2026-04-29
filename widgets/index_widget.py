import os
from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QTableWidget, QTableWidgetItem, QFrame,
    QMessageBox, QHeaderView
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from db import get_conn

class IndexWidget(QWidget):
    view_item = Signal(int) 
    edit_item = Signal(int)

    def __init__(self):
        super().__init__()
        self.current_user_role = "" 
        self.setup_ui()

    def set_user_data(self, fullname, role):
        """Menerima data dari login. Role dipastikan huruf kecil."""
        self.lbl_admin.setText(f"Hallo, {fullname}")
        self.current_user_role = str(role).lower().strip() 
        self.refresh_list()

    def setup_ui(self):
        base_dir = os.path.dirname(os.path.dirname(__file__))
        bg_path = os.path.join(base_dir, "assets", "bg_dashboard.jpg")
        self.bg = QLabel(self)
        if os.path.exists(bg_path):
            self.bg.setPixmap(QPixmap(bg_path)) 
        self.bg.setScaledContents(True)
        self.bg.lower() 

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(40, 40, 40, 40)
        self.card = QFrame() 
        # Card Utama (Latar belakang putih transparan)
        self.card.setStyleSheet("QFrame { background-color: rgba(255, 255, 255, 0.9); border-radius: 30px; }")
        root_layout.addWidget(self.card)
        
        layout = QVBoxLayout(self.card)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        header_layout = QHBoxLayout()
        # FIX: Dashboard Title tanpa kotak belakang
        title = QLabel("Dashboard")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #1a1a1a; background: transparent; border: none;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # FIX: Label Hallo tanpa kotak belakang
        self.lbl_admin = QLabel("Hallo, User") 
        self.lbl_admin.setStyleSheet("font-size: 16px; color: #555; font-weight: bold; background: transparent; border: none;")
        header_layout.addWidget(self.lbl_admin)

        self.btn_logout = QPushButton("Logout")
        self.btn_logout.setFixedSize(80, 30)
        self.btn_logout.setStyleSheet("QPushButton { background-color: #f8f9fa; border: 1px solid #dc3545; color: #dc3545; border-radius: 8px; font-weight: bold; }")
        header_layout.addWidget(self.btn_logout)
        layout.addLayout(header_layout)
        
        self.search = QLineEdit()
        self.search.setPlaceholderText("Cari SKU / nama / barcode...")
        self.search.setFixedHeight(45)
        self.search.setStyleSheet("QLineEdit { border-radius: 12px; padding-left: 15px; color: black; background: white; border: 1px solid #ddd; }")
        self.search.textChanged.connect(self.refresh_list) 
        layout.addWidget(self.search)

        button_layout = QHBoxLayout()
        self.btn_add = QPushButton("+ Tambah Barang") 
        self.btn_add.setFixedSize(160, 40)
        self.btn_add.setStyleSheet("background-color: #0d6efd; color: white; border-radius: 10px; font-weight: bold;")
        button_layout.addWidget(self.btn_add)
        
        self.btn_scan = QPushButton("Scan Barcode")
        self.btn_scan.setFixedSize(140, 40)
        self.btn_scan.setStyleSheet("background-color: #ffc107; color: #212529; border-radius: 10px; font-weight: bold;")
        button_layout.addWidget(self.btn_scan)
        
        self.btn_manage_users = QPushButton("Kelola User")
        self.btn_manage_users.setFixedSize(130, 40)
        self.btn_manage_users.setStyleSheet("background-color: #6c757d; color: white; border-radius: 10px; font-weight: bold;")
        button_layout.addWidget(self.btn_manage_users)
        
        button_layout.addStretch(1)
        layout.addLayout(button_layout)
        
        # FIX: Total Stok tanpa kotak belakang
        self.lbl_total_stok = QLabel("Total Nilai Stok: Rp 0")
        self.lbl_total_stok.setStyleSheet("font-size: 16px; font-weight: bold; color: #28a745; background: transparent; border: none;")
        layout.addWidget(self.lbl_total_stok)

        self.table = QTableWidget(0, 9)
        self.table.setHorizontalHeaderLabels(["SKU", "Nama", "Barcode", "Lokasi", "Qty", "Harga", "Nilai", "Diubah Oleh", "Aksi"])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers) 
        self.table.setWordWrap(True)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(7, QHeaderView.Stretch)
        header.setSectionResizeMode(8, QHeaderView.Fixed); self.table.setColumnWidth(8, 220)
        
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet("QTableWidget { background-color: white; color: black; gridline-color: #eee; border: none; }")
        layout.addWidget(self.table)
        
    def refresh_list(self):
        if self.current_user_role == "admin" or self.current_user_role == "administrator":
             self.btn_manage_users.show()
        else:
             self.btn_manage_users.hide()

        query_text = self.search.text().strip()
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                sql_base = "SELECT id, sku, name, barcode, location, qty, price, last_updated_by FROM items "
                if query_text:
                    sql = sql_base + "WHERE sku LIKE %s OR name LIKE %s OR barcode LIKE %s ORDER BY id DESC"
                    param = f"%{query_text}%"
                    cur.execute(sql, (param, param, param))
                else:
                    cur.execute(sql_base + "ORDER BY id DESC")
                rows = cur.fetchall()
            
            self.table.setRowCount(len(rows))
            total_nilai = 0
            for row_idx, row_data in enumerate(rows):
                qty, harga = row_data.get('qty', 0), float(row_data.get('price', 0))
                total_nilai += (qty * harga)
                self.table.setItem(row_idx, 0, QTableWidgetItem(str(row_data['sku'])))
                self.table.setItem(row_idx, 1, QTableWidgetItem(str(row_data['name'])))
                self.table.setItem(row_idx, 2, QTableWidgetItem(str(row_data.get('barcode', '-'))))
                self.table.setItem(row_idx, 3, QTableWidgetItem(str(row_data.get('location', '-'))))
                self.table.setItem(row_idx, 4, QTableWidgetItem(str(qty)))
                self.table.setItem(row_idx, 5, QTableWidgetItem(f"Rp {harga:,.0f}"))
                self.table.setItem(row_idx, 6, QTableWidgetItem(f"Rp {qty*harga:,.0f}"))
                self.table.setItem(row_idx, 7, QTableWidgetItem(str(row_data.get('last_updated_by') or "-")))
                self.setup_actions(row_idx, row_data['id'])
                
            self.lbl_total_stok.setText(f"Total Nilai Stok: Rp {total_nilai:,.0f}")
        finally:
            conn.close()

    def setup_actions(self, row, item_id):
        action_widget = QWidget()
        h_layout = QHBoxLayout(action_widget)
        h_layout.setContentsMargins(5, 5, 5, 5)
        
        btn_view = QPushButton("View")
        btn_view.setStyleSheet("background-color: #0dcaf0; color: white; border-radius: 5px; font-weight: bold;")
        btn_view.clicked.connect(lambda _, id=item_id: self.view_item.emit(id)) 
        h_layout.addWidget(btn_view)
        
        btn_edit = QPushButton("Edit")
        btn_edit.setStyleSheet("background-color: #6c757d; color: white; border-radius: 5px; font-weight: bold;")
        btn_edit.clicked.connect(lambda _, id=item_id: self.edit_item.emit(id))
        h_layout.addWidget(btn_edit)
        
        btn_del = QPushButton("Hapus")
        if self.current_user_role == "operator":
            btn_del.hide()
        else:
            btn_del.setStyleSheet("background-color: #dc3545; color: white; border-radius: 8px; font-weight: bold;")
            btn_del.clicked.connect(lambda _, id=item_id: self.handle_delete(id))
            
        h_layout.addWidget(btn_del)
        self.table.setCellWidget(row, 8, action_widget)
        self.table.setRowHeight(row, 50)

    def handle_delete(self, item_id):
        confirm = QMessageBox.question(self, 'Konfirmasi', f"Hapus produk ID {item_id}?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            conn = get_conn()
            try:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM items WHERE id = %s", (item_id,))
                    conn.commit()
                self.refresh_list()
            finally:
                conn.close()

    def resizeEvent(self, event):
        if hasattr(self, 'bg'): self.bg.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)