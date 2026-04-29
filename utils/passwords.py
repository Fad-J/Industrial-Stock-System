# utils/passwords.py
# File ini berfungsi untuk mengelola hashing dan verifikasi password
# dengan beberapa metode (bcrypt, werkzeug, dan fallback terakhir)

# Rekomendasi instalasi library:
# pip install passlib[bcrypt] werkzeug

try:
    # ================================
    # OPSI UTAMA (PALING AMAN)
    # Menggunakan passlib dengan bcrypt
    # ================================
    from passlib.hash import bcrypt

    # Fungsi untuk meng-hash password
    def hash_password(pw: str) -> str:
        # bcrypt.hash otomatis menambahkan salt dan cost factor
        return bcrypt.hash(pw)

    # Fungsi untuk memverifikasi password
    def verify_password(pw: str, hashed: str) -> bool:
        # Membandingkan password input dengan hash tersimpan
        return bcrypt.verify(pw, hashed)

except Exception:
    # Jika passlib tidak tersedia, masuk ke opsi kedua
    try:
        # ================================
        # OPSI ALTERNATIF
        # Menggunakan werkzeug.security
        # ================================
        from werkzeug.security import generate_password_hash, check_password_hash

        # Fungsi untuk meng-hash password
        def hash_password(pw: str) -> str:
            # Menggunakan pbkdf2:sha256 secara default
            return generate_password_hash(pw)

        # Fungsi untuk memverifikasi password
        def verify_password(pw: str, hashed: str) -> bool:
            # Mengecek kecocokan password dengan hash
            return check_password_hash(hashed, pw)

    except Exception:
        # ==========================================
        # OPSI TERAKHIR (FALLBACK DARURAT)
        # TIDAK DISARANKAN UNTUK PRODUCTION
        # ==========================================
        import hashlib, os

        # Fungsi untuk meng-hash password secara manual
        def hash_password(pw: str) -> str:
            # Membuat salt acak sepanjang 8 byte
            salt = os.urandom(8).hex()

            # Menggabungkan salt dan password lalu di-hash SHA-256
            h = hashlib.sha256((salt + pw).encode()).hexdigest()

            # Format penyimpanan hash:
            # sha256$<salt>$<hash>
            return f"sha256${salt}${h}"

        # Fungsi untuk memverifikasi password
        def verify_password(pw: str, hashed: str) -> bool:
            try:
                # Memisahkan metode, salt, dan hash
                method, salt, hv = hashed.split("$", 2)

                # Jika metode bukan sha256, langsung gagal
                if method != "sha256":
                    return False

                # Meng-hash ulang password input dengan salt yang sama
                import hashlib
                return hashlib.sha256((salt + pw).encode()).hexdigest() == hv

            except Exception:
                # Jika format hash salah atau error lain
                return False
