# 📚 Buku Kas Keuangan Pribadi

Aplikasi pencatatan dan pengelolaan keuangan pribadi modern berbasis **FastAPI**, **SQLite**, dan **Single-Page Web Frontend** (HTML/CSS/JS + Chart.js).

---

## 🌟 Fitur Utama
- 📊 **Ringkasan Keuangan**: Saldo real-time, statistik pemasukan & pengeluaran.
- 💸 **Pencatatan Transaksi**: Catat Pemasukan & Pengeluaran dengan kategori & tanggal.
- 🎯 **Target Tabungan (Goals)**: Pantau progres tabungan dalam persen (%).
- 💰 **Manajemen Anggaran (Budgets)**: Batasi pengeluaran per kategori.
- 📈 **Visualisasi Grafik**: Grafik pengeluaran per kategori dan tren saldo.

---

## 📂 Struktur Proyek

```text
buku-kas-app/
├── app/
│   ├── __init__.py
│   ├── main.py            # Entry point FastAPI & penyaji HTML
│   ├── database.py        # Koneksi Database SQLite
│   ├── models.py          # Tabel ORM Database
│   ├── schemas.py         # Skema Validasi Pydantic
│   └── routers/
│       ├── __init__.py
│       ├── transactions.py
│       ├── goals.py
│       └── budgets.py
├── static/
│   └── index.html         # Tampilan Web & Logika JS
├── requirements.txt       # Dependencies Python
└── README.md              # Dokumentasi Proyek