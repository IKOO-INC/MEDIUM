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
