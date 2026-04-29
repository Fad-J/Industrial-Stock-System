import os
from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, 
    QVBoxLayout, QHBoxLayout, QFrame, QMessageBox, 
    QDoubleSpinBox, QSpinBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap

# Hubungkan dengan koneksi database Anda
from db import get_conn

class AddItemWidget(QWidget):
    back_to_dashboard = Signal()
    item_added = Signal()  
    cancelled = Signal()   

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        base_dir = os.path.dirname(os.path.dirname(__file__))
        bg_path = os.path.join(base_dir, "assets", "bg_dashboard.jpg")
        
        self.bg = QLabel(self)
        self.bg.setPixmap(QPixmap(bg_path))
        self.bg.setScaledContents(True)
        self.bg.lower()

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)

        self.card = QFrame()
        self.card.setObjectName("formCard")
        self.card.setFixedWidth(900)
        self.card.setStyleSheet("""
            QFrame#formCard {
                background-color: #ffffff;
                border-radius: 25px;
            }
            QLabel { font-weight: bold; color: #333; font-size: 14px; }
            QLineEdit, QSpinBox, QDoubleSpinBox {
                background-color: #f8f9fa;
                border: 1px solid #ccc;
                border-radius: 10px;
                padding: 10px;
                font-size: 15px;
            }
            /* Menghilangkan panah tambah kurang yang jelek */
            QSpinBox::up-button, QSpinBox::down-button,
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                width: 0px;
            }
        """)
        
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(20)

        # Judul
        title = QLabel("Tambah Barang")
        title.setStyleSheet("font-size: 30px; font-weight: bold;")
        card_layout.addWidget(title)

        self.btn_back_link = QPushButton("← Kembali ke Dashboard")
        self.btn_back_link.setStyleSheet("text-align: left; color: #0d6efd; border: none; font-weight: bold; background: transparent;")
        self.btn_back_link.clicked.connect(lambda: self.cancelled.emit())
        card_layout.addWidget(self.btn_back_link)

        # Baris 1: SKU & Nama
        row1 = QHBoxLayout()
        col_sku = QVBoxLayout(); col_sku.addWidget(QLabel("SKU *"))
        self.input_sku = QLineEdit(); col_sku.addWidget(self.input_sku)
        row1.addLayout(col_sku)

        col_nama = QVBoxLayout(); col_nama.addWidget(QLabel("Nama Barang *"))
        self.input_nama = QLineEdit(); col_nama.addWidget(self.input_nama)
        row1.addLayout(col_nama)
        card_layout.addLayout(row1)

        # Baris 2: Barcode, Lokasi, Qty
        row2 = QHBoxLayout()
        col_bar = QVBoxLayout(); col_bar.addWidget(QLabel("Barcode"))
        self.input_barcode = QLineEdit(); col_bar.addWidget(self.input_barcode)
        row2.addLayout(col_bar, 2)

        col_lok = QVBoxLayout(); col_lok.addWidget(QLabel("Lokasi"))
        self.input_lokasi = QLineEdit(); col_lok.addWidget(self.input_lokasi)
        row2.addLayout(col_lok, 1)

        col_qty = QVBoxLayout(); col_qty.addWidget(QLabel("Qty Awal"))
        self.input_qty = QSpinBox(); self.input_qty.setRange(0, 999999); self.input_qty.setFixedHeight(42)
        col_qty.addWidget(self.input_qty)
        row2.addLayout(col_qty, 1)
        card_layout.addLayout(row2)

        # Baris 3: Harga
        price_container = QWidget(); price_container.setFixedWidth(350)
        col_price = QVBoxLayout(price_container); col_price.setContentsMargins(0,0,0,0)
        col_price.addWidget(QLabel("Harga / item (Rp)"))
        self.input_harga = QDoubleSpinBox(); self.input_harga.setRange(0, 999999999); self.input_harga.setDecimals(0); self.input_harga.setFixedHeight(42)
        col_price.addWidget(self.input_harga)
        card_layout.addWidget(price_container)

        # Tombol Simpan & Batal
        btn_layout = QHBoxLayout()
        self.btn_simpan = QPushButton("Simpan")
        self.btn_simpan.setFixedSize(140, 45)
        self.btn_simpan.setStyleSheet("background-color: #0d6efd; color: white; border-radius: 12px; font-weight: bold;")
        self.btn_simpan.clicked.connect(self.save_data) # HUBUNGKAN KE FUNGSI SAVE
        
        self.btn_batal = QPushButton("Batal")
        self.btn_batal.setFixedSize(110, 45)
        self.btn_batal.setStyleSheet("background-color: #f1f3f5; border-radius: 12px; font-weight: bold;")
        self.btn_batal.clicked.connect(lambda: self.cancelled.emit())

        btn_layout.addWidget(self.btn_simpan); btn_layout.addWidget(self.btn_batal)
        card_layout.addLayout(btn_layout)

        main_layout.addWidget(self.card)

    def save_data(self):
        """Fungsi untuk menyimpan data ke MySQL phpMyAdmin"""
        sku = self.input_sku.text().strip()
        nama = self.input_nama.text().strip()
        barcode = self.input_barcode.text().strip()
        lokasi = self.input_lokasi.text().strip()
        qty = self.input_qty.value()
        harga = self.input_harga.value()

        if not sku or not nama:
            QMessageBox.warning(self, "Peringatan", "SKU dan Nama Barang wajib diisi!")
            return

        conn = get_conn()
        try:
            with conn.cursor() as cur:
                # Sesuaikan nama kolom dengan phpMyAdmin Anda (name, location, price)
                sql = "INSERT INTO items (sku, name, barcode, location, qty, price) VALUES (%s, %s, %s, %s, %s, %s)"
                cur.execute(sql, (sku, nama, barcode, lokasi, qty, harga))
                conn.commit()
                
            QMessageBox.information(self, "Sukses", "Data barang berhasil disimpan!")
            self.item_added.emit() # Memberitahu main.py untuk refresh dashboard
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Error", f"Gagal menyimpan data: {str(e)}")
        finally:
            conn.close()

    def resizeEvent(self, event):
        if hasattr(self, 'bg'): self.bg.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)