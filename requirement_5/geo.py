from __future__ import annotations
from pathlib import Path
from typing import Optional, Tuple, Dict
import re
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = PROJECT_ROOT / "data" / "processed"

def first_author(full_authors: str) -> str:
    # divide por ' and ' (BibTeX) o comas/semicolon si viniera plano
    if not full_authors: return ""
    parts = re.split(r"\s+and\s+|;|,", full_authors)
    return parts[0].strip()

def infer_country(row: pd.Series, aff_map: Optional[pd.DataFrame]) -> str:
    # prioridad explícita
    if isinstance(row.get("country",""), str) and row["country"]:
        return row["country"]
    # intenta a partir de affiliation/address/institution
    aff_text = " ".join([str(row.get("affiliation","")), str(row.get("authors",""))]).lower()
    if aff_map is not None and not aff_map.empty:
        # buscar coincidencia por 'institution' simple (archivo externo: institution,country)
        for pat, country in zip(aff_map["institution"], aff_map["country"]):
            try:
                if pat.lower() in aff_text:
                    return country
            except Exception:
                pass
    # heurística simple por lista de países (pycountry opcional)
    try:
        import pycountry  # type: ignore
        for c in pycountry.countries:
            if c.name.lower() in aff_text:
                return c.name
            for n in getattr(c, "official_name", ""), *[a for a in getattr(c, "alt_spellings", [])]:
                if isinstance(n,str) and n and n.lower() in aff_text:
                    return c.name
    except Exception:
        pass
    return "Unknown"

def compute_country_counts(df: pd.DataFrame, aff_map_csv: Optional[Path] = None) -> pd.DataFrame:
    aff_map = None
    if aff_map_csv and Path(aff_map_csv).exists():
        aff_map = pd.read_csv(aff_map_csv)
    firsts = df["authors"].map(first_author)
    countries = df.apply(lambda r: infer_country(r, aff_map), axis=1)
    out = pd.DataFrame({"first_author": firsts, "country": countries})
    counts = out.groupby("country").size().reset_index(name="count")
    counts = counts[counts["country"] != "Unknown"].sort_values("count", ascending=False)
    return counts

def plot_world_heatmap(counts: pd.DataFrame, out_png: Path, out_html: Path):
    try:
        import plotly.express as px  # type: ignore
        fig = px.choropleth(
            counts, locations="country", locationmode="country names",
            color="count", color_continuous_scale="Blues",
            title="Mapa de calor por país del primer autor"
        )
        fig.update_layout(margin=dict(l=0,r=0,t=60,b=0))
        # HTML interactivo
        fig.write_html(str(out_html))
        # PNG estático (requiere kaleido)
        try:
            fig.write_image(str(out_png), scale=2)
        except Exception:
            # fallback: guardar HTML solamente
            pass
        return True
    except Exception:
        # Fallback: gráfico de barras (matplotlib)
        import matplotlib.pyplot as plt
        
        # Mostrar todos los países
        counts_plot = counts.copy()
        n_countries = len(counts_plot)
        
        # Ajustar tamaño de figura según cantidad de países
        # Aproximadamente 0.3 pulgadas por país, mínimo 8
        fig_width = max(16, n_countries * 0.3)
        fig_height = 10
        
        plt.figure(figsize=(fig_width, fig_height))
        plt.bar(range(n_countries), counts_plot["count"], color='steelblue')
        plt.xticks(range(n_countries), counts_plot["country"], 
                   rotation=90, ha="center", fontsize=8)
        plt.xlabel("País", fontsize=11)
        plt.ylabel("Número de publicaciones", fontsize=11)
        plt.title(f"Primer autor por país (conteo) - {n_countries} países", 
                  fontsize=13, fontweight='bold')
        plt.grid(axis='y', alpha=0.3, linestyle='--')
        plt.tight_layout()
        plt.savefig(out_png, dpi=200, bbox_inches='tight')
        plt.close()
        return False
