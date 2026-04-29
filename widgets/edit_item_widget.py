import os
from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, 
    QVBoxLayout, QHBoxLayout, QFrame, QMessageBox, 
    QDoubleSpinBox, QSpinBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from db import get_conn

class EditItemWidget(QWidget):
    back_to_dashboard = Signal()
    item_updated = Signal()

    def __init__(self, item_id=None, current_user="Unknown"):
        super().__init__()
        self.item_id = item_id 
        self.current_user = current_user # Mengambil fullname dari MainWindow
        self.setup_ui()
        
        if self.item_id:
            self.load_item_data(self.item_id)

    def setup_ui(self):
        base_dir = os.path.dirname(os.path.dirname(__file__))
        bg_path = os.path.join(base_dir, "assets", "bg_dashboard.jpg")
        
        self.bg = QLabel(self)
        if os.path.exists(bg_path):
            self.bg.setPixmap(QPixmap(bg_path))
        self.bg.setScaledContents(True)
        self.bg.lower()

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)

        self.card = QFrame()
        self.card.setObjectName("editCard")
        self.card.setFixedWidth(900)
        self.card.setStyleSheet("""
            QFrame#editCard {
                background-color: rgba(255, 255, 255, 0.95);
                border-radius: 25px;
                border: 1px solid #ddd;
            }
            QLabel { font-weight: bold; color: #333; font-size: 14px; background: transparent; }
            QLineEdit, QSpinBox, QDoubleSpinBox {
                background-color: #f8f9fa;
                border: 1px solid #ccc;
                border-radius: 10px;
                padding: 10px;
                font-size: 15px;
                color: #333;
            }
            QSpinBox::up-button, QSpinBox::down-button,
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button { width: 0px; }
        """)
        
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(20)

        title = QLabel("Edit Barang & Riwayat Stok/Harga")
        title.setStyleSheet("font-size: 30px; font-weight: bold; color: #111; background: transparent;")
        card_layout.addWidget(title)

        # Baris 1: SKU & Nama
        row1 = QHBoxLayout()
        row1.setSpacing(20)
        col_sku = QVBoxLayout(); col_sku.addWidget(QLabel("SKU *"))
        self.input_sku = QLineEdit(); col_sku.addWidget(self.input_sku); row1.addLayout(col_sku)
        col_nama = QVBoxLayout(); col_nama.addWidget(QLabel("Nama Barang *"))
        self.input_nama = QLineEdit(); col_nama.addWidget(self.input_nama); row1.addLayout(col_nama)
        card_layout.addLayout(row1)

        # Baris 2: Barcode, Lokasi, Qty
        row2 = QHBoxLayout()
        row2.setSpacing(20)
        col_bar = QVBoxLayout(); col_bar.addWidget(QLabel("Barcode"))
        self.input_barcode = QLineEdit(); col_bar.addWidget(self.input_barcode); row2.addLayout(col_bar, 2)
        col_lok = QVBoxLayout(); col_lok.addWidget(QLabel("Lokasi"))
        self.input_lokasi = QLineEdit(); col_lok.addWidget(self.input_lokasi); row2.addLayout(col_lok, 1)
        col_qty = QVBoxLayout(); col_qty.addWidget(QLabel("Qty Stok"))
        self.input_qty = QSpinBox(); self.input_qty.setRange(0, 999999); self.input_qty.setFixedHeight(42); col_qty.addWidget(self.input_qty); row2.addLayout(col_qty, 1)
        card_layout.addLayout(row2)

        # Baris 3: Harga
        price_container = QWidget(); price_container.setFixedWidth(350); price_container.setStyleSheet("background: transparent;")
        col_price = QVBoxLayout(price_container); col_price.setContentsMargins(0,0,0,0); col_price.addWidget(QLabel("Harga / item (Rp)"))
        self.input_harga = QDoubleSpinBox(); self.input_harga.setRange(0, 999999999); self.input_harga.setDecimals(0); self.input_harga.setFixedHeight(42); col_price.addWidget(self.input_harga)
        card_layout.addWidget(price_container)

        # Tombol Aksi
        btn_layout = QHBoxLayout(); btn_layout.setSpacing(15)
        self.btn_save = QPushButton("Simpan Perubahan"); self.btn_save.setFixedSize(200, 45); self.btn_save.setCursor(Qt.PointingHandCursor); self.btn_save.setStyleSheet("background-color: #0d6efd; color: white; border-radius: 12px; font-weight: bold; font-size: 15px;"); self.btn_save.clicked.connect(self.update_data); btn_layout.addWidget(self.btn_save)
        self.btn_cancel = QPushButton("Batal"); self.btn_cancel.setFixedSize(110, 45); self.btn_cancel.setCursor(Qt.PointingHandCursor); self.btn_cancel.setStyleSheet("background-color: #f1f3f5; border-radius: 12px; font-weight: bold; border: 1px solid #ccc; color: black;"); self.btn_cancel.clicked.connect(lambda: self.back_to_dashboard.emit()); btn_layout.addWidget(self.btn_cancel)
        card_layout.addLayout(btn_layout)

        main_layout.addWidget(self.card)

    def load_item_data(self, item_id):
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM items WHERE id = %s", (item_id,))
                item = cur.fetchone()
                if item:
                    self.input_sku.setText(str(item.get('sku', '')))
                    self.input_nama.setText(str(item.get('name', '')))
                    self.input_barcode.setText(str(item.get('barcode', '')))
                    self.input_lokasi.setText(str(item.get('location', '')))
                    self.input_qty.setValue(int(item.get('qty', 0)))
                    self.input_harga.setValue(float(item.get('price', 0)))
        finally:
            conn.close()

    def update_data(self):
        """Audit trail: Menghitung selisih stok dan mencatat User ID dengan benar"""
        if self.item_id is None: return
        sku, name = self.input_sku.text().strip(), self.input_nama.text().strip()
        new_qty, new_price = self.input_qty.value(), self.input_harga.value()

        if not sku or not name:
            QMessageBox.warning(self, "Peringatan", "SKU dan Nama Barang wajib diisi!")
            return

        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT qty, price FROM items WHERE id = %s", (self.item_id,))
                old_data = cur.fetchone()
                old_qty, old_price = old_data.get('qty', 0), float(old_data.get('price', 0))
                
                # FIX: Hitung selisih agar tidak 'None'
                selisih_stok = new_qty - old_qty

                # Update data barang + audit pengubah
                sql_update = "UPDATE items SET sku=%s, name=%s, barcode=%s, location=%s, qty=%s, price=%s, last_updated_by=%s WHERE id=%s"
                cur.execute(sql_update, (sku, name, self.input_barcode.text(), self.input_lokasi.text(), new_qty, new_price, self.current_user, self.item_id))

                # Catat history jika ada perubahan
                if selisih_stok != 0 or new_price != old_price:
                    reason = ""
                    if selisih_stok != 0: reason += f"Update stok dari {old_qty} ke {new_qty}. "
                    if new_price != old_price: reason += f"Harga berubah: Rp {old_price:,.0f} -> Rp {new_price:,.0f}."
                    
                    # FIX: Simpan nama user ke 'user_id_name'
                    sql_history = "INSERT INTO stock_movements (item_id, user_id_name, change_amount, reason) VALUES (%s, %s, %s, %s)"
                    cur.execute(sql_history, (self.item_id, self.current_user, selisih_stok, reason))

                conn.commit()
                QMessageBox.information(self, "Sukses", f"Perubahan disimpan oleh {self.current_user}!")
                self.item_updated.emit()
                self.back_to_dashboard.emit()
        except Exception as e:
            if conn: conn.rollback()
            QMessageBox.critical(self, "Error", f"Gagal update: {e}")
        finally:
            if conn: conn.close()

    def resizeEvent(self, event):
        if hasattr(self, 'bg'): self.bg.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)