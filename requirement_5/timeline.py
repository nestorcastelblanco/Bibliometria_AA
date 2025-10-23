from __future__ import annotations
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

def to_int_year(s) -> int | None:
    try:
        y = int(str(s)[:4])
        if 1900 <= y <= 2100: return y
    except Exception:
        return None
    return None

def plot_year_series(df: pd.DataFrame, out_png: Path):
    years = df["year"].map(to_int_year).dropna().astype(int)
    ser = years.value_counts().sort_index()
    plt.figure(figsize=(12,5))
    plt.plot(ser.index, ser.values, marker="o")
    plt.title("Publicaciones por año")
    plt.xlabel("Año"); plt.ylabel("Cantidad")
    plt.grid(True, axis="y", alpha=0.3)
    plt.tight_layout(); plt.savefig(out_png, dpi=220)

def plot_journal_series(df: pd.DataFrame, out_png: Path, top_n: int = 8):
    tmp = df.copy()
    tmp["year"] = tmp["year"].map(to_int_year)
    tmp = tmp.dropna(subset=["year"])
    tmp["year"] = tmp["year"].astype(int)
    top = tmp["journal"].value_counts().head(top_n).index.tolist()
    tmp["journal_top"] = tmp["journal"].where(tmp["journal"].isin(top), "Otros")
    piv = tmp.pivot_table(index="year", columns="journal_top", values="title", aggfunc="count").fillna(0)
    ax = piv.plot(kind="area", stacked=True, figsize=(12,6))
    ax.set_title("Publicaciones por año y revista (Top {})".format(top_n))
    ax.set_xlabel("Año"); ax.set_ylabel("Cantidad")
    plt.tight_layout(); plt.savefig(out_png, dpi=220); plt.close()
