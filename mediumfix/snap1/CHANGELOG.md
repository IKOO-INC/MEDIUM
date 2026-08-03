# Perubahan mediumfix

## Yang diubah

- Seluruh file HTML di folder `templates/` diubah tampilannya menggunakan gaya Adminator.
- `templates/base.html` diubah menjadi layout Adminator dengan sidebar, topbar, footer, dark mode, dan navigasi responsif.
- Asset tema ditempatkan di `static/adminator/`.
- Ditambahkan `static/adminator/medium.css` untuk penyesuaian komponen khusus project.
- Ditambahkan `static/adminator/medium.js` untuk dark mode, tanggal, dan sidebar mobile.
- File `2026-original.js` disimpan sebagai referensi asset asli template, tetapi tidak dimuat karena berisi menu dan link halaman demo Adminator.

## Yang tidak diubah

- `app.py`
- Semua route Flask
- Koneksi dan query MongoDB
- Nama field form
- Nama variabel Jinja
- Struktur data dan logika aplikasi
- `requirements.txt`

## Catatan

Tidak ada perubahan kode Python. Semua penyesuaian berada di HTML, CSS, dan JavaScript tampilan.

## Update Fitur Absensi QR

### Route baru
- `GET/POST /attendance/manual` — form absensi manual.
- `GET /attendance/scan` — halaman scanner kamera QR.
- `GET/POST /attendance/scan/<qr_token>` — konfirmasi anggota hasil scan dan input keterangan.
- `GET /members/qr` — halaman cetak semua QR anggota.
- `GET /members/qr/<qr_token>.png` — gambar QR individual / unduh PNG.

### Perubahan data
- Setiap anggota sekarang memiliki field `qr_token` unik.
- Anggota lama yang masih berupa string atau belum memiliki token akan dimigrasikan otomatis saat halaman anggota/absensi dibuka.
- Catatan absensi baru memiliki field `method` dengan nilai `manual` atau `scan`.
- Absensi hasil scan juga menyimpan `qr_token` anggota.

### File baru
- `templates/attendance_manual.html`
- `templates/attendance_scan.html`
- `templates/attendance_scan_member.html`
- `templates/member_qr.html`

### File yang diperbarui
- `app.py` — helper QR, migrasi anggota, route terpisah, generator QR PNG.
- `templates/base.html` — menu Rekap Absensi, Absen Manual, dan Scan QR dipisahkan.
- `templates/attendance.html` — menjadi halaman rekap/statistik serta menampilkan metode absensi.
- `templates/members.html` — tombol cetak/unduh QR.
- `static/adminator/medium.css` — tampilan scanner, konfirmasi, kartu QR, dan layout cetak.
- `requirements.txt` — menambahkan `qrcode[pil]==8.2`.

### Catatan scanner
- Scanner menggunakan `html5-qrcode` dari CDN dan memiliki fallback BarcodeDetector bawaan browser serta input URL/token manual.
- Kamera browser umumnya memerlukan HTTPS saat aplikasi dipasang di domain publik. `localhost` tetap dapat digunakan saat pengembangan.

## 2026-08-02 — Perbaikan layout Grid QR Scan

- Memperbaiki bug layout pada halaman Scan QR dan halaman lain yang menggunakan kelas grid `col-4`, `col-5`, `col-7`, atau `col-8`.
- Menambahkan definisi span 4/5/7/8 kolom pada CSS custom.
- Menambahkan breakpoint responsif agar kolom-kolom tersebut otomatis menjadi full-width pada layar <= 1100px.
- Tidak mengubah `app.py`, route, database, atau logika absensi.
