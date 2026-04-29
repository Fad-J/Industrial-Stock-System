# Import fungsi koneksi database dari db.py
from db import get_conn


# ===============================
# INSERT ITEM
# ===============================
def insert_item(sku, name, barcode, location, qty, price, user_id=0):
    # Membuka koneksi ke database
    conn = get_conn()
    try:
        # Memulai transaksi (agar bisa rollback jika gagal)
        conn.begin()
        with conn.cursor() as cur:
            # Menyimpan data item baru ke tabel items
            cur.execute(
                """
                INSERT INTO items (sku, name, barcode, location, qty, price)
                VALUES (%s,%s,%s,%s,%s,%s)
                """,
                (sku, name, barcode, location, qty, price)
            )

            # Mengambil ID item yang baru saja diinsert
            new_id = cur.lastrowid

            # Jika stok awal tidak nol, catat ke tabel stock_movements
            if qty != 0:
                cur.execute(
                    """
                    INSERT INTO stock_movements
                    (item_id, change_amount, user_id, reason)
                    VALUES (%s,%s,%s,%s)
                    """,
                    (new_id, qty, user_id, "initial_stock")
                )

        # Menyimpan semua perubahan ke database
        conn.commit()

        # Mengembalikan ID item baru
        return new_id
    except Exception:
        # Membatalkan semua perubahan jika terjadi error
        conn.rollback()
        raise
    finally:
        # Menutup koneksi database
        conn.close()


# ===============================
# GET SINGLE ITEM
# ===============================
def get_item(item_id):
    # Membuka koneksi database
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            # Mengambil satu data item berdasarkan ID
            cur.execute("SELECT * FROM items WHERE id=%s", (item_id,))
            return cur.fetchone()
    finally:
        # Menutup koneksi
        conn.close()


# ===============================
# UPDATE ITEM (POSITIONAL ARGUMENTS)
# ===============================
def update_item(
    item_id,
    sku,
    name,
    barcode,
    location,
    qty,
    price,
    user_id
):
    # Membuka koneksi database
    conn = get_conn()
    try:
        # Memulai transaksi
        conn.begin()
        with conn.cursor() as cur:
            # Mengambil stok lama dari item
            cur.execute("SELECT qty FROM items WHERE id=%s", (item_id,))
            row = cur.fetchone()

            # Jika item tidak ditemukan, lempar error
            if not row:
                raise Exception("Item tidak ditemukan")

            # Menghitung selisih stok baru dan lama
            old_qty = int(row["qty"])
            diff = qty - old_qty

            # Update data item
            cur.execute(
                """
                UPDATE items
                SET sku=%s,
                    name=%s,
                    barcode=%s,
                    location=%s,
                    qty=%s,
                    price=%s
                WHERE id=%s
                """,
                (sku, name, barcode, location, qty, price, item_id)
            )

            # Jika ada perubahan stok, simpan ke tabel stock_movements
            if diff != 0:
                cur.execute(
                    """
                    INSERT INTO stock_movements
                    (item_id, change_amount, user_id, reason)
                    VALUES (%s,%s,%s,%s)
                    """,
                    (item_id, diff, user_id, "edit_item")
                )

        # Menyimpan perubahan
        conn.commit()
        return True
    except Exception:
        # Batalkan transaksi jika terjadi kesalahan
        conn.rollback()
        raise
    finally:
        # Menutup koneksi database
        conn.close()


# ===============================
# DELETE ITEM
# ===============================
def delete_item(item_id):
    # Membuka koneksi database
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            # Menghapus item berdasarkan ID
            cur.execute("DELETE FROM items WHERE id=%s", (item_id,))
        # Menyimpan perubahan
        conn.commit()
        return True
    except Exception:
        # Batalkan jika gagal
        conn.rollback()
        raise
    finally:
        # Menutup koneksi
        conn.close()


# ===============================
# LIST ITEMS
# ===============================
def list_items(q: str = "", limit: int = 500):
    # Membuka koneksi database
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            # Menyiapkan parameter pencarian LIKE
            like = f"%{q}%"

            # Mengambil daftar item berdasarkan SKU, nama, atau barcode
            cur.execute(
                """
                SELECT * FROM items
                WHERE sku LIKE %s OR name LIKE %s OR barcode LIKE %s
                ORDER BY name
                LIMIT %s
                """,
                (like, like, like, limit)
            )
            return cur.fetchall()
    finally:
        # Menutup koneksi
        conn.close()


# ===============================
# TOTAL STOCK VALUE
# ===============================
def total_stock_value():
    # Membuka koneksi database
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            # Menghitung total nilai stok (qty * price)
            cur.execute("SELECT SUM(qty * price) AS total_value FROM items")
            r = cur.fetchone()

            # Jika NULL, kembalikan 0
            return float(r["total_value"] or 0)
    finally:
        # Menutup koneksi
        conn.close()


# ===============================
# ADJUST STOCK
# ===============================
def adjust_stock(item_id: int, delta: int, reason: str = "manual", user_id: int = 0):
    # Membuka koneksi database
    conn = get_conn()
    try:
        # Memulai transaksi
        conn.begin()
        with conn.cursor() as cur:
            # Update stok item (tidak boleh kurang dari 0)
            cur.execute(
                "UPDATE items SET qty = GREATEST(0, qty + %s) WHERE id=%s",
                (delta, item_id)
            )

            # Mencatat perubahan stok
            cur.execute(
                """
                INSERT INTO stock_movements
                (item_id, change_amount, user_id, reason)
                VALUES (%s,%s,%s,%s)
                """,
                (item_id, delta, user_id, reason)
            )

        # Menyimpan perubahan
        conn.commit()
        return True
    except Exception:
        # Batalkan transaksi jika error
        conn.rollback()
        raise
    finally:
        # Menutup koneksi database
        conn.close()


# ===============================
# FIND ITEM BY BARCODE / SKU
# ===============================
def find_item_by_barcode_or_sku(code: str):
    # Membuka koneksi database
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            # Mencari item berdasarkan barcode atau SKU
            cur.execute(
                """
                SELECT id, sku, name, barcode, location, qty, price
                FROM items
                WHERE barcode=%s OR sku=%s
                LIMIT 1
                """,
                (code, code)
            )
            return cur.fetchone()
    finally:
        # Menutup koneksi
        conn.close()


# ===============================
# ITEM + STOCK MOVEMENTS
# ===============================
def get_item_with_movements(item_id: int):
    # Membuka koneksi database
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            # Mengambil data item
            cur.execute(
                """
                SELECT id, sku, name, barcode, location, qty, price
                FROM items
                WHERE id=%s
                """,
                (item_id,)
            )
            item = cur.fetchone()

            # Jika item tidak ditemukan
            if not item:
                return None

            # Mengambil riwayat pergerakan stok
            cur.execute(
                """
                SELECT change_amount, reason, created_at
                FROM stock_movements
                WHERE item_id=%s
                ORDER BY created_at DESC
                """,
                (item_id,)
            )

            # Menyimpan riwayat stok ke dalam dict item
            item["movements"] = cur.fetchall()
            return item
    finally:
        # Menutup koneksi database
        conn.close()
