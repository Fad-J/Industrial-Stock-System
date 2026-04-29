# 📦 Industrial Stock System

![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![PySide6](https://img.shields.io/badge/PySide6-41CD52?logo=qt&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-4479A1?logo=mysql&logoColor=white)
![Status](https://img.shields.io/badge/status-active-brightgreen)

> Aplikasi desktop manajemen stok industri dengan fitur login, QR Code scanner, dan manajemen pengguna — dibangun menggunakan Python & PySide6.

---

## ✨ Fitur

- 🔐 **Autentikasi** — Login dengan enkripsi password menggunakan `bcrypt`
- 📊 **Dashboard Stok** — Lihat, tambah, edit, dan hapus data barang
- 📷 **Scan QR Code** — Identifikasi barang via webcam menggunakan `pyzbar` & `OpenCV`
- 👤 **Manajemen User** — Kelola akun pengguna dengan role (admin/user)
- 🖨️ **Generate QR Code** — Buat QR Code otomatis untuk setiap barang
- 🎨 **UI Modern** — Tampilan antarmuka dengan custom styling PySide6

---

## 🛠️ Teknologi

| Teknologi | Kegunaan |
|---|---|
| Python 3 | Bahasa pemrograman utama |
| PySide6 | Framework GUI desktop |
| PyMySQL | Koneksi ke database MySQL/MariaDB |
| OpenCV (`opencv-python`) | Akses webcam untuk scan barcode |
| pyzbar | Decode QR Code / Barcode |
| qrcode[pil] | Generate gambar QR Code |
| bcrypt | Enkripsi & verifikasi password |
| numpy | Pemrosesan array gambar |
| colorama | Warna output terminal |

---

## 📁 Struktur Project

```
python/
├── main.py                  # Entry point utama aplikasi
├── db.py                    # Konfigurasi & koneksi database
├── auth.py                  # Logika autentikasi login
├── models.py                # Model data & query database
├── styles.py                # Styling UI aplikasi
├── assets/
│   ├── bg_login.jpg         # Background halaman login
│   └── bg_dashboard.jpg     # Background dashboard
├── widgets/
│   ├── login_widget.py      # Halaman login
│   ├── index_widget.py      # Dashboard utama / daftar stok
│   ├── add_item_widget.py   # Form tambah barang
│   ├── edit_item_widget.py  # Form edit barang
│   ├── view_item_widget.py  # Detail barang
│   ├── scan_widget.py       # Scanner QR Code via webcam
│   └── user_widget.py       # Manajemen pengguna
├── utils/
│   └── passwords.py         # Helper enkripsi password
└── sql/
    └── industrial_stock.sql # File SQL untuk setup database
```

---

## 🚀 Cara Menjalankan

### 1. Install Dependencies

Buka terminal di VS Code, lalu jalankan:

```bash
pip install PySide6 opencv-python PyMySQL qrcode[pil] bcrypt pyzbar numpy colorama
```

> ⚠️ Pastikan koneksi internet stabil saat proses instalasi.

---

### 2. Setup Database

1. Buka **phpMyAdmin** (via XAMPP atau sejenisnya)
2. Buat database baru bernama `industrial_stock`
3. Import file SQL: `sql/industrial_stock.sql`

---

### 3. Konfigurasi Koneksi Database

Buka file `db.py` dan sesuaikan konfigurasi jika diperlukan:

```python
DB_HOST = "localhost"
DB_USER = "root"
DB_PASS = ""           # Sesuaikan dengan password MySQL kamu
DB_NAME = "industrial_stock"
DB_PORT = 3306
```

---

### 4. Buat & Aktifkan Virtual Environment

```bash
# Buat virtual environment
python -m venv env

# Aktifkan (Windows PowerShell)
.\env\Scripts\Activate.ps1

# Aktifkan (Windows CMD)
env\Scripts\activate.bat

# Aktifkan (Mac/Linux)
source env/bin/activate
```

> ✅ Berhasil jika muncul tulisan `(env)` di sebelah kiri terminal.

---

### 5. Jalankan Aplikasi

```bash
python main.py
```

---

## ⚠️ Catatan Penting

- Pastikan **XAMPP / MySQL** aktif sebelum menjalankan program
- Pastikan **webcam** aktif dan tidak dipakai aplikasi lain untuk fitur Scan QR Code
- Gunakan **Python 3.10+** untuk kompatibilitas terbaik dengan PySide6
- File `db.py` berisi konfigurasi database lokal — **jangan di-push ke repo publik** jika password tidak kosong

---

## 👨‍💻 Developer

Dibuat oleh **[Fad-J](https://github.com/Fad-J)**
