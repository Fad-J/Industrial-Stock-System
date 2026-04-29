# db.py - koneksi database untuk aplikasi Python (padanan db.php)

# Import library pymysql untuk koneksi MySQL/MariaDB
import pymysql

# Import DictCursor agar hasil query berbentuk dictionary (key = nama kolom)
from pymysql.cursors import DictCursor

# ==============
# CREDENTIAL DATABASE (SAMA SEPERTI PHP)
# ==============

# Host database (biasanya localhost jika pakai XAMPP)
DB_HOST = "localhost"

# Username database MySQL
DB_USER = "root"

# Password database (XAMPP default biasanya kosong)
DB_PASS = ""

# Nama database yang digunakan
DB_NAME = "industrial_stock"

# Port MySQL (default 3306, ubah jika berbeda)
DB_PORT = 3306


# ============================
#  FUNGSI KONEKSI DATABASE
# ============================
def get_conn():
    """
    Fungsi untuk membuat dan mengembalikan koneksi database.

    Padanan PHP:
    $conn = new mysqli($host, $user, $pass, $db);

    Jika koneksi gagal, maka akan melempar exception
    (mirip mysqli_report / die() di PHP).
    """

    try:
        # Membuat koneksi ke database MySQL
        conn = pymysql.connect(
            host=DB_HOST,  # alamat server database
            user=DB_USER,  # username database
            password=DB_PASS,  # password database
            database=DB_NAME,  # nama database
            port=DB_PORT,  # port MySQL
            charset="utf8mb4",  # support karakter unicode (emoji, dll)

            # Cursor berbentuk dictionary
            # Contoh: row["username"] bukan row[0]
            cursorclass=DictCursor,

            # Autocommit dimatikan agar transaksi manual
            # Mirip dengan PHP yang pakai commit() / rollback()
            autocommit=False
        )

        # Jika berhasil, kembalikan objek koneksi
        return conn

    except Exception as e:
        # Menampilkan pesan error jika koneksi gagal
        print("Database connection failed:", e)

        # Melempar ulang error ke level atas
        # Mirip PHP yang menghentikan program dengan error
        raise
