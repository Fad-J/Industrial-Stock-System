-- =====================================================
-- phpMyAdmin SQL Dump
-- =====================================================
-- Versi phpMyAdmin yang digunakan
-- Server: MariaDB 10.4.32
-- PHP Version: 8.2.12
-- Waktu generate database
-- =====================================================

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
-- Mengatur agar kolom AUTO_INCREMENT tidak otomatis bernilai 0

START TRANSACTION;
-- Memulai transaksi database (agar bisa rollback jika error)

SET time_zone = "+00:00";
-- Mengatur zona waktu database ke UTC

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
-- Menyimpan charset lama client

/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
-- Menyimpan charset hasil query lama

/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
-- Menyimpan collation lama

/*!40101 SET NAMES utf8mb4 */;
-- Mengatur charset menjadi utf8mb4 (support emoji & karakter internasional)

-- =====================================================
-- Database: industrial_stock
-- =====================================================

-- -----------------------------------------------------
-- Struktur tabel: items
-- -----------------------------------------------------
-- Tabel ini menyimpan data barang/stok
-- -----------------------------------------------------

CREATE TABLE `items` (
  `id` int(11) NOT NULL,
  -- ID unik setiap item

  `sku` varchar(50) DEFAULT NULL,
  -- Kode SKU barang

  `name` varchar(100) DEFAULT NULL,
  -- Nama barang

  `barcode` varchar(100) DEFAULT NULL,
  -- Barcode barang

  `location` varchar(50) DEFAULT NULL,
  -- Lokasi penyimpanan barang

  `qty` int(11) DEFAULT 0,
  -- Jumlah stok barang

  `price` decimal(15,2) NOT NULL DEFAULT 0.00,
  -- Harga barang

  `last_updated_by` varchar(255) DEFAULT NULL
  -- Nama user terakhir yang mengupdate data
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_general_ci;

-- -----------------------------------------------------
-- Data awal untuk tabel items
-- -----------------------------------------------------

INSERT INTO `items`
(`id`, `sku`, `name`, `barcode`, `location`, `qty`, `price`, `last_updated_by`)
VALUES
(2, 'SHT-045', 'Steel Sheet 2mm', '890123400002', 'B2-10', 50, 2500.00, 'operator magang'),
(3, 'NUT-M8', 'Nut M8', '890123400003', 'A1-02', 500, 1000.00, 'operator magang'),
(4, 'OIL-5L', 'Hydraulic Oil 5L', '890123400012', 'C3-05', 29, 10000.00, 'Administrator'),
(17, '233', 'rty', '1111', 'V1', 2022, 1000.00, 'Administrator');

-- =====================================================
-- Struktur tabel: price_history
-- =====================================================
-- Menyimpan riwayat perubahan harga barang
-- =====================================================

CREATE TABLE `price_history` (
  `id` int(11) NOT NULL,
  -- ID riwayat harga

  `item_id` int(11) NOT NULL,
  -- ID item yang harganya berubah

  `old_price` decimal(15,2) NOT NULL,
  -- Harga lama

  `new_price` decimal(15,2) NOT NULL,
  -- Harga baru

  `user_id` int(11) NOT NULL,
  -- ID user yang mengubah harga

  `changed_at` datetime NOT NULL DEFAULT current_timestamp()
  -- Waktu perubahan harga
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_general_ci;

-- -----------------------------------------------------
-- Data riwayat perubahan harga
-- -----------------------------------------------------

INSERT INTO `price_history`
(`id`, `item_id`, `old_price`, `new_price`, `user_id`, `changed_at`)
VALUES
(1, 9, 2000.00, 1000.43, 3, '2025-11-30 11:11:51'),
(2, 9, 1000.43, 1000.66, 3, '2025-11-30 11:33:07'),
(3, 9, 1000.66, 1000.70, 1, '2025-11-30 11:33:41'),
(4, 9, 1000.70, 5000.00, 1, '2025-11-30 11:35:54'),
(5, 9, 5000.00, 5149.00, 1, '2025-11-30 11:43:43');

-- =====================================================
-- Struktur tabel: stock_movements
-- =====================================================
-- Mencatat setiap perubahan stok barang
-- =====================================================

CREATE TABLE `stock_movements` (
  `id` int(11) NOT NULL,
  -- ID transaksi stok

  `item_id` int(11) DEFAULT NULL,
  -- ID item yang berubah stoknya

  `user_id_name` varchar(255) DEFAULT NULL,
  -- Nama user (opsional)

  `change_amount` int(11) DEFAULT NULL,
  -- Jumlah perubahan stok (+/-)

  `user_id` int(11) DEFAULT NULL,
  -- ID user yang melakukan perubahan

  `reason` varchar(255) DEFAULT NULL,
  -- Alasan perubahan stok

  `created_at` datetime DEFAULT current_timestamp()
  -- Waktu perubahan stok
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_general_ci;

-- =====================================================
-- Struktur tabel: users
-- =====================================================
-- Menyimpan data akun pengguna sistem
-- =====================================================

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  -- ID user

  `username` varchar(50) NOT NULL,
  -- Username login

  `password` varchar(255) NOT NULL,
  -- Password (hash bcrypt)

  `role` enum('admin','operator') NOT NULL DEFAULT 'operator',
  -- Role user

  `fullname` varchar(100) DEFAULT NULL
  -- Nama lengkap user
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_general_ci;

-- =====================================================
-- Index & Primary Key
-- =====================================================

ALTER TABLE `items`
  ADD PRIMARY KEY (`id`);

ALTER TABLE `price_history`
  ADD PRIMARY KEY (`id`);

ALTER TABLE `stock_movements`
  ADD PRIMARY KEY (`id`),
  ADD KEY `item_id` (`item_id`);

ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

-- =====================================================
-- AUTO_INCREMENT
-- =====================================================

ALTER TABLE `items`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=18;

ALTER TABLE `price_history`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

ALTER TABLE `stock_movements`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=59;

ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

-- =====================================================
-- Foreign Key Constraint
-- =====================================================

ALTER TABLE `stock_movements`
  ADD CONSTRAINT `stock_movements_ibfk_1`
  FOREIGN KEY (`item_id`) REFERENCES `items` (`id`)
  ON DELETE CASCADE
  ON UPDATE CASCADE;
-- Jika item dihapus, data pergerakan stok ikut terhapus

COMMIT;
-- Menyimpan semua perubahan ke database

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
