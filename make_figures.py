"""Regenerate every figure in the BVK working paper.

Gambar 1-8 are rebuilt from the workbooks in ``fig/`` using the DEN house style
(``fig_den``); Gambar 9-10 are designed infographics that exist only as bitmaps
inside the Word draft, so they are copied out of the docx package verbatim.
The draft is not distributed with this repository; ``fig/fig09.png`` and
``fig/fig10.png`` are shipped as-is and left untouched when it is absent.
Gambar 11-12 are built from ``data/dampak_bvk_neraca_jasa.csv``.

Run from the repository root::

    python make_figures.py
"""

from __future__ import annotations

import io
import zipfile
from pathlib import Path

import fig_den as den
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
FIG = ROOT / "fig"
DOCX = ROOT / "docx" / "[Draft] Working Paper_Kebijakan BVK_310826_vFinal.docx"

# den.cls sets b5paper with 1.7 cm side margins, so the text block is 14.2 cm.
# The paper places Gambar 1-8 two-up, leaving each panel about 6.7 cm (2.6 in)
# wide. Authoring small with oversized type keeps the labels legible once LaTeX
# scales the panel down, which shrinking a default 10x6 figure would not.
FIGSIZE = (5.2, 3.6)
FIGSIZE_WIDE = (10.4, 4.0)
# Gambar 9-10 run the full 14.2 cm text width; authoring them at twice that
# prints the source note at the same size as on the two-up panels.
INFOGRAPHIC_WIDTH = 11.2

# Gambar 1, 2 and 7 stay inside the DEN core palette: Gold for the comparator
# countries, Red to pull Indonesia out of the field.
HIGHLIGHT = den.RED
BASE = den.GOLD
EDGE = den.DARK_BROWN

SRC_BI = "Sumber: Bank Indonesia, CEIC (diolah DEN)"
SRC_BPS = "Sumber: BPS, CEIC (diolah DEN)"
SRC_DEN = "Sumber: Estimasi DEN"


def _out(name: str) -> Path:
    return FIG / name


def _stamp_source(fig, source: str) -> None:
    """Right-align the source note with the axes, just below the lowest artist.

    Rotated tick labels push the drawn extent below the axes, so the note is
    anchored to the rendered bounding box rather than a fixed figure coordinate.
    """
    fig.draw_without_rendering()
    bottom_in = fig.get_tightbbox().y0
    right = max(ax.get_position().x1 for ax in fig.axes)
    fig.text(
        right,
        (bottom_in - 0.04) / fig.get_figheight(),
        source,
        ha="right",
        va="top",
        fontsize=9,
        fontstyle="italic",
        color=den.GREY,
    )


def _save(fig, name: str, source: str) -> None:
    _stamp_source(fig, source)
    path = _out(name)
    den.save(fig, path)
    print(f"wrote {path.relative_to(ROOT)}")


def _annotate_signed(ax, bars, values, *, fmt="{:.1f}", fontsize=9):
    """Value labels that sit above positive bars and below negative ones."""
    for b, val in zip(bars, values):
        above = val >= 0
        ax.annotate(
            fmt.format(val),
            xy=(b.get_x() + b.get_width() / 2, b.get_height()),
            xytext=(0, 4 if above else -4),
            textcoords="offset points",
            ha="center",
            va="bottom" if above else "top",
            fontsize=fontsize,
            fontweight="bold",
        )


def fig01_nilai_tukar() -> None:
    """Gambar 1. Perubahan nilai tukar terhadap dolar AS (YtD, %)."""
    df = pd.read_excel(
        FIG / "Fig 1 - ER thdp USD.xlsx",
        sheet_name="Fig 1",
        usecols="A:B",
        nrows=14,
        names=["negara", "ytd"],
        header=0,
    ).dropna(subset=["negara", "ytd"])
    df = df[df["negara"] != "Turki"].sort_values("ytd")

    colors = [HIGHLIGHT if n == "Indonesia" else BASE for n in df["negara"]]

    # den.bar collapses a colour list to its first entry, so the per-bar
    # highlight is drawn directly and annotated with the DEN helper.
    fig, ax = den.subplots(figsize=FIGSIZE)
    bars = ax.bar(df["negara"], df["ytd"], color=colors, width=0.65)
    _annotate_signed(ax, bars, df["ytd"], fmt="{:.1f}", fontsize=7)
    den.hline(ax, 0)
    den.label(ax, ylabel="%")
    ax.tick_params(axis="x", labelrotation=90)
    _save(fig, "fig01.png", SRC_BI)


def fig02_cad_nilai_tukar() -> None:
    """Gambar 2. CAB dan nilai tukar negara ASEAN (kuadran)."""
    NUDGE = {
        "Thailand": (7, 4),
        "Filipina": (-8, -12),
        "India": (7, -3),
        "Indonesia": (7, -11),
    }
    raw = pd.read_excel(
        FIG / "Fig 2 - CAD vs Nilai Tukar.xlsx",
        sheet_name="Fig 2",
        usecols="A,B,D",
        nrows=7,
        names=["cad", "kurs", "negara"],
        header=0,
    ).dropna(subset=["negara"])

    fig, ax = den.subplots(figsize=FIGSIZE)
    for _, row in raw.iterrows():
        highlight = row["negara"] == "Indonesia"
        ax.scatter(
            row["cad"],
            row["kurs"],
            s=90 if highlight else 60,
            color=HIGHLIGHT if highlight else BASE,
            edgecolor=HIGHLIGHT if highlight else EDGE,
            linewidth=0.8,
            zorder=3,
        )
        ax.annotate(
            row["negara"],
            (row["cad"], row["kurs"]),
            textcoords="offset points",
            xytext=NUDGE.get(row["negara"], (7, 4)),
            fontsize=8,
            fontweight="bold" if highlight else "normal",
            color=HIGHLIGHT if highlight else den.GREY,
        )

    den.hline(ax, 0)
    den.vline(ax, 0, color="gray", linestyle="--")
    den.label(ax, xlabel="Transaksi berjalan (% PDB)", ylabel="Nilai tukar (YtD, %)")
    ax.margins(x=0.18, y=0.18)
    _save(fig, "fig02.png", SRC_BI)


def fig03_neraca_berjalan() -> None:
    """Gambar 3. Komponen neraca transaksi berjalan (USD miliar)."""
    df = pd.read_excel(FIG / "Fig 4 - Neraca.xlsx", sheet_name="Fig 4 - Neraca")
    df.columns = [str(c).strip() for c in df.columns]
    # "Tw. III 2023" -> "III ’23" so twelve quarter labels fit a half-width panel.
    df["Quarter"] = df["Quarter"].map(
        lambda q: q.replace("Tw. ", "").replace(" 20", " ’")
    )

    components = ["Barang", "Jasa", "Pendapatan Primer", "Pendapatan Sekunder"]
    colors = [den.GOLD, den.RED, den.DARK_BROWN, den.TAN]

    # The four components sum exactly to the current account, so they stack;
    # den.stacked_bar carries a single bottom accumulator and would overlay the
    # deficit components on the surplus ones, hence the signed stacking here.
    fig, ax = den.subplots(figsize=FIGSIZE)
    x = np.arange(len(df))
    pos = np.zeros(len(df))
    neg = np.zeros(len(df))
    for col, color in zip(components, colors):
        vals = df[col].to_numpy(dtype=float)
        ax.bar(x, vals, bottom=np.where(vals >= 0, pos, neg), width=0.72,
               color=color, label=col)
        pos += np.clip(vals, 0, None)
        neg += np.clip(vals, None, 0)

    # Net balance is the sum of the stack, not the top of any bar, so it is
    # marked rather than drawn as a line.
    ax.plot(
        x,
        df["Neraca Transaksi Berjalan"],
        linestyle="none",
        marker="D",
        markersize=5,
        color=den.GREY,
        markeredgecolor="white",
        markeredgewidth=0.7,
        label="Neraca Transaksi Berjalan",
        zorder=4,
    )

    den.hline(ax, 0)
    den.label(ax, ylabel="USD miliar")
    ax.set_xticks(x)
    ax.set_xticklabels(df["Quarter"])
    ax.tick_params(axis="x", labelrotation=90)
    den.legend_top(ax, ncol=2)
    _save(fig, "fig03.png", SRC_BI)


def fig04_neraca_barang() -> None:
    """Gambar 4. Neraca perdagangan barang bulanan (USD miliar)."""
    df = pd.read_excel(
        FIG / "Fig 4a - Barang.xlsx",
        sheet_name="Sheet1",
        usecols="A:D",
        names=["bulan", "Migas", "Nonmigas", "Neraca Perdagangan"],
        header=0,
    ).dropna(subset=["bulan"])
    df["bulan"] = pd.to_datetime(df["bulan"])

    fig, ax = den.subplots(figsize=FIGSIZE)
    ax.bar(df["bulan"], df["Nonmigas"], width=22, color=den.GOLD, label="Nonmigas")
    ax.bar(df["bulan"], df["Migas"], width=22, color=den.SLATE_BLUE, label="Migas")
    ax.plot(
        df["bulan"],
        df["Neraca Perdagangan"],
        color=den.RED,
        linewidth=1.8,
        label="Neraca perdagangan",
        zorder=4,
    )
    den.hline(ax, 0)
    den.label(ax, ylabel="USD miliar")
    ax.tick_params(axis="x", labelrotation=90)
    den.legend_top(ax, ncol=3)
    _save(fig, "fig04.png", SRC_BPS)


def _grouped_2019_2025(workbook: str, sheet: str, ylabel: str, out: str) -> None:
    df = pd.read_excel(
        FIG / workbook,
        sheet_name=sheet,
        usecols="A:C",
        nrows=5,
        names=["negara", "2019", "2025"],
        header=0,
    ).dropna(subset=["negara"])

    fig, ax = den.subplots(figsize=FIGSIZE)
    den.grouped_bar(
        ax, df, x="negara", y_cols=["2019", "2025"], fmt="{:.1f}", legend=False
    )
    den.label(ax, ylabel=ylabel)
    ax.tick_params(axis="x", labelrotation=30)
    for lbl in ax.get_xticklabels():
        lbl.set_horizontalalignment("right")
    den.legend_top(ax, ncol=2)
    _save(fig, out, SRC_BPS)


def fig05_kedatangan_wisman() -> None:
    """Gambar 5. Jumlah kedatangan wisman (juta orang)."""
    _grouped_2019_2025(
        "Fig 5 - Kedatangan Wisman.xlsx", "Fi g5", "Juta orang", "fig05.png"
    )


def fig06_devisa_pariwisata() -> None:
    """Gambar 6. Penerimaan devisa pariwisata (% PDB)."""
    _grouped_2019_2025(
        "Fig 6 - Devisa Pariwisata.xlsx", "Sheet1", "% terhadap PDB", "fig06.png"
    )


def fig07_negara_bebas_visa() -> None:
    """Gambar 7. Jumlah negara penerima bebas visa (terkini)."""
    df = pd.read_excel(
        FIG / "Fig 7 - Negara Visa.xlsx",
        sheet_name="Sheet1",
        usecols="A:B",
        nrows=6,
        names=["negara", "jumlah"],
        header=0,
    ).dropna(subset=["negara"])
    df = df.sort_values("jumlah", ascending=False)

    colors = [HIGHLIGHT if n == "Indonesia" else BASE for n in df["negara"]]

    fig, ax = den.subplots(figsize=FIGSIZE)
    bars = ax.bar(df["negara"], df["jumlah"], color=colors, width=0.6)
    den.annotate_bars(ax, bars, df["jumlah"], fmt="{:.0f}")
    den.label(ax, ylabel="Jumlah negara")
    ax.tick_params(axis="x", labelrotation=45)
    _save(
        fig, "fig07.png", "Sumber: Kementerian Imigrasi masing-masing negara"
    )


def fig08_kumulatif_tiongkok() -> None:
    """Gambar 8. Total kumulatif negara bebas visa Tiongkok."""
    df = pd.read_excel(
        FIG / "Fig 8 - Kumulatif bebas visa china.xlsx",
        sheet_name="Fig 1",
        usecols="A:B",
        names=["tanggal", "kumulatif"],
        header=0,
    ).dropna()
    df["tanggal"] = pd.to_datetime(df["tanggal"])

    fig, ax = den.subplots(figsize=FIGSIZE)
    ax.step(df["tanggal"], df["kumulatif"], where="post", color=den.GOLD, linewidth=2)
    ax.fill_between(
        df["tanggal"], df["kumulatif"], step="post", color=den.GOLD, alpha=0.18
    )
    last = df.iloc[-1]
    ax.annotate(
        f"{int(last['kumulatif'])}",
        (last["tanggal"], last["kumulatif"]),
        textcoords="offset points",
        xytext=(-14, 6),
        fontweight="bold",
        color=den.DARK_BROWN,
    )
    den.label(ax, ylabel="Jumlah negara (kumulatif)")
    ax.tick_params(axis="x", labelrotation=45)
    _save(fig, "fig08.png", "Sumber: Kementerian Luar Negeri RRT")


def figs09_10_from_docx() -> None:
    """Gambar 9-10. Infografik peta jalan dan peta pintu masuk-DPSP."""
    if not DOCX.exists():
        print("skipped fig09.png, fig10.png (Word draft not distributed)")
        return
    media = {"word/media/image1.png": "fig09.png", "word/media/image2.png": "fig10.png"}
    with zipfile.ZipFile(DOCX) as z:
        for member, out in media.items():
            img = plt.imread(io.BytesIO(z.read(member)), format="png")
            height, width = img.shape[:2]
            fig, ax = den.subplots(
                figsize=(INFOGRAPHIC_WIDTH, INFOGRAPHIC_WIDTH * height / width)
            )
            ax.set_position([0, 0, 1, 1])
            ax.imshow(img, interpolation="lanczos")
            ax.axis("off")
            _save(fig, out, "Sumber: DEN, diolah")


def _ekspor_jasa_bar(value: str, ylabel: str, fmt: str, out: str) -> None:
    """Dampak murni BVK vs agregat per skenario dan case, dari CSV di ``data/``.

    ``pct_pdb`` memakai PDB nominal 2026 sebesar USD 1.443,13 miliar: PDB ADHB
    2025 (BPS) ditumbuhkan dengan asumsi APBN 2026 (riil 5,4%, inflasi 2,5%).
    """
    df = pd.read_csv(ROOT / "data" / "dampak_bvk_neraca_jasa.csv")
    df["kategori"] = df["jumlah_negara"].astype(str) + " negara\n" + df["case"]
    wide = (
        df.pivot(index="kategori", columns="basis", values=value)
        .reindex(df["kategori"].unique())
        .rename(columns={"BVK": "Dampak murni BVK"})
        .reset_index()
    )

    fig, ax = den.subplots(figsize=FIGSIZE)
    den.grouped_bar(
        ax,
        wide,
        x="kategori",
        y_cols=["Dampak murni BVK", "Agregat"],
        colors=[den.GOLD, den.DARK_BROWN],
        annotate=False,
        legend=False,
    )
    # grouped_bar's fixed 8 pt labels collide across the pair at three decimals.
    for bars in ax.containers:
        ax.bar_label(bars, fmt=fmt, padding=2, fontsize=7, fontweight="bold")
    den.label(ax, ylabel=ylabel)
    ax.tick_params(axis="x", labelsize=9)
    den.legend_top(ax, ncol=2)
    _save(fig, out, SRC_DEN)


def fig11_ekspor_jasa() -> None:
    """Gambar 11. Tambahan ekspor jasa perjalanan akibat BVK (USD miliar)."""
    _ekspor_jasa_bar("ekspor_jasa_usd_miliar", "USD miliar", "{:.2f}", "fig11.png")


def fig12_ekspor_jasa_pdb() -> None:
    """Gambar 12. Tambahan ekspor jasa perjalanan akibat BVK (% PDB)."""
    _ekspor_jasa_bar("pct_pdb", "% terhadap PDB", "{:.3f}", "fig12.png")


def main() -> None:
    den.style(font_scale=1.35)
    fig01_nilai_tukar()
    fig02_cad_nilai_tukar()
    fig03_neraca_berjalan()
    fig04_neraca_barang()
    fig05_kedatangan_wisman()
    fig06_devisa_pariwisata()
    fig07_negara_bebas_visa()
    fig08_kumulatif_tiongkok()
    figs09_10_from_docx()
    fig11_ekspor_jasa()
    fig12_ekspor_jasa_pdb()


if __name__ == "__main__":
    main()
