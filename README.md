## Introduction

Repositori ini memuat naskah dan bahan replikasi untuk DEN Working Paper No. 6, "Kebijakan Bebas Visa
Kunjungan untuk Memperkuat Penerimaan Devisa dan Neraca Transaksi Berjalan".

Kajian menilai potensi perluasan Kebijakan Bebas Visa Kunjungan (BVK) sebagai instrumen untuk
meningkatkan kunjungan wisatawan mancanegara, memperkuat penerimaan devisa pariwisata, dan
mendukung ketahanan neraca transaksi berjalan, dengan tetap memperhitungkan dampak fiskal dan
risiko keimigrasian.

Pertanyaan mengenai repositori ini dapat dikirim ke ryanginting(at)dewanekonomi.go.id.

## Cara menggunakan repo ini

### Requirements

- Python (kami menggunakan distribusi Anaconda) dengan paket `pandas`, `numpy`, `matplotlib`, `openpyxl`, dan [`fig-den`](https://github.com/den-econ/fig-den).
- Quarto (>= 1.2) dan distribusi LaTeX untuk merender naskah dengan format [laporan DEN](https://github.com/den-econ/wp).

### Langkah

1. `python make_figures.py` membaca data di folder `fig/` dan `data/`, lalu menulis ulang gambar ke `fig/`. Gambar 9 dan 10 adalah infografik dan disertakan sebagai berkas PNG.
2. `quarto render pariwisata.qmd` menghasilkan `pariwisata.pdf`.

### Struktur folder

| Folder/berkas | Isi |
|---|---|
| `pariwisata.qmd` | Naskah utama |
| `pariwisata.pdf` | Naskah hasil render |
| `make_figures.py` | Skrip pembuat Gambar 1–12 |
| `fig/` | Berkas Excel sumber setiap gambar, beserta PNG hasil `make_figures.py` |
| `data/` | Hasil estimasi dampak BVK terhadap ekspor jasa perjalanan (sumber Gambar 11–12) |
| `table/` | Data seluruh tabel naskah dalam format CSV (`table_01` hingga `table_19`) |
| `_extensions/` | Ekstensi format Quarto untuk artikel DEN |

## Sitasi

Sitasi yang dapat digunakan adalah:

Ginting, R. A., Ramadhan, G., Kainama, N. P., Fatah, M. H. A., & Vinastya, S. T. M. 2026. Kebijakan Bebas Visa Kunjungan untuk Memperkuat Penerimaan Devisa dan Neraca Transaksi Berjalan. DEN Working Paper No. 6.

atau jika anda menggunakan bibtex:

```bibtex
@article{ginting2026bvk,
  author  = {Ginting, Ryan Alfaedison and Ramadhan, Gaffari and Kainama, Nasya Putri and Fatah, Muhammad Husni Abdul and Vinastya, Sevi Tyas Murti},
  title   = {Kebijakan Bebas Visa Kunjungan untuk Memperkuat Penerimaan Devisa dan Neraca Transaksi Berjalan},
  journal = {DEN Working Paper},
  year    = {2026},
  volume  = {6},
  url     = {https://github.com/den-econ/pariwisata}
}
```

## Lisensi dan Hak Cipta
Seluruh aset, kode, dan data dalam repositori ini dilindungi di bawah **Lisensi DEN**.

Penggunaan, penggandaan, atau pendistribusian materi di dalam repositori ini harus mematuhi ketentuan yang tercantum dalam file **[LICENSE](LICENSE)**.

*Hak Cipta (c) 2026 Dewan Ekonomi Nasional Republik Indonesia (DEN)*
