# auth.py - autentikasi untuk aplikasi GUI (padanan auth.php)
# File ini berfungsi sebagai sistem autentikasi sederhana
# untuk aplikasi GUI Python (misalnya PySide6 / Tkinter)

class Auth:
    """
    Kelas Auth berfungsi sebagai sistem autentikasi sederhana.
    Menggantikan mekanisme session pada PHP.
    Data user yang login disimpan sementara di memory aplikasi.
    """

    # Variabel class untuk menyimpan user yang sedang login
    # Contoh isi:
    # {"id": 1, "username": "admin", "role": "admin"}
    _current_user = None

    # =============================
    #  LOGIN & LOGOUT
    # =============================

    @classmethod
    def login(cls, user_dict: dict):
        """
        Method untuk login user.

        Parameter:
        user_dict → dictionary data user yang berhasil login,
        minimal harus berisi:
        {
            "id": int,
            "username": str,
            "role": str
        }
        """
        # Menyimpan data user ke variabel class _current_user
        cls._current_user = user_dict

    @classmethod
    def logout(cls):
        """
        Method untuk logout user.
        Menghapus data user dari memory (session di-reset).
        """
        cls._current_user = None

    # =============================
    #  SESSION-LIKE ACCESSOR
    # =============================

    @classmethod
    def current_user(cls):
        """
        Mengembalikan data user yang sedang login.
        Jika belum ada user yang login, mengembalikan None.
        """
        return cls._current_user

    @classmethod
    def is_authenticated(cls):
        """
        Mengecek apakah user sudah login atau belum.

        Return:
        True  → jika user sudah login
        False → jika belum login
        """
        return cls._current_user is not None

    # =============================
    #  AUTH CHECK (padanan require_login)
    # =============================

    @classmethod
    def require_login(cls):
        """
        Padanan fungsi require_login() pada PHP.

        Pada aplikasi GUI (PySide6 / Tkinter),
        fungsi ini hanya mengembalikan nilai True atau False,
        sedangkan penanganan UI (redirect, message box, dll)
        dilakukan oleh widget yang memanggilnya.
        """
        return cls._current_user is not None

    # =============================
    #  ROLE CHECK
    # =============================

    @classmethod
    def require_role(cls, role: str):
        """
        Mengecek apakah user memiliki role tertentu.

        Parameter:
        role → role yang dibutuhkan (contoh: 'admin')

        Return:
        True  → jika user login dan role sesuai
        False → jika user belum login atau role tidak sesuai
        """
        # Jika tidak ada user yang login
        if not cls._current_user:
            return False

        # Mengecek apakah role user sama dengan role yang diminta
        return cls._current_user.get("role") == role

    @classmethod
    def is_admin(cls):
        """
        Padanan fungsi is_admin() pada PHP.

        Return:
        True  → jika user login dan memiliki role 'admin'
        False → jika bukan admin atau belum login
        """
        return (
            cls._current_user is not None and
            cls._current_user.get("role") == "admin"
        )
