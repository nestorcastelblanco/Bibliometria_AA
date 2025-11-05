"""
Módulo para análisis geográfico y generación de mapas de calor por país.

Funcionalidades:
- Extracción del primer autor de listas de autores
- Inferencia de países desde afiliaciones o metadata
- Generación de mapas de calor interactivos (Plotly) o estáticos (Matplotlib)
- Soporte para mapeo manual institution→country via CSV
"""
from __future__ import annotations
from pathlib import Path
from typing import Optional, Tuple, Dict
import re
import pandas as pd

# Rutas del proyecto
PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = PROJECT_ROOT / "data" / "processed"

def first_author(full_authors: str) -> str:
    """
    Extrae el nombre del primer autor de una lista de autores BibTeX.
    
    Maneja múltiples formatos de separación de autores:
    - BibTeX estándar: "Author1 and Author2 and Author3"
    - Separados por comas: "Author1, Author2, Author3"
    - Separados por punto y coma: "Author1; Author2; Author3"
    
    Args:
        full_authors (str): String con lista completa de autores
    
    Returns:
        str: Nombre del primer autor, string vacío si no hay autores
    
    Example:
        >>> first_author("John Smith and Jane Doe and Bob Wilson")
        'John Smith'
        >>> first_author("Smith, J.; Doe, J.; Wilson, B.")
        'Smith, J.'
        >>> first_author("")
        ''
    
    Notas:
        - Divide por ' and ' (BibTeX estándar)
        - También divide por ';' o ',' si no hay ' and '
        - Retorna el primer elemento después de dividir
        - Limpia espacios en blanco al inicio y final
    """
    if not full_authors: 
        return ""
    
    # Dividir por múltiples separadores posibles
    parts = re.split(r"\s+and\s+|;|,", full_authors)
    return parts[0].strip()

def infer_country(row: pd.Series, aff_map: Optional[pd.DataFrame]) -> str:
    """
    Infiere el país de un artículo usando metadata de afiliación y autores.
    
    Estrategia de inferencia (en orden de prioridad):
    1. Campo 'country' explícito si existe
    2. Mapeo manual institution→country desde CSV externo
    3. Búsqueda de nombres de países en affiliation/authors usando pycountry
    4. Retorna "Unknown" si no encuentra coincidencia
    
    Args:
        row (pd.Series): Fila del DataFrame con campos 'country', 'affiliation', 'authors'
        aff_map (Optional[pd.DataFrame]): DataFrame con columnas ['institution', 'country']
                                         para mapeo manual
    
    Returns:
        str: Nombre del país inferido o "Unknown"
    
    Proceso:
        1. Si existe campo 'country' no vacío, usarlo directamente
        2. Construir texto de búsqueda: affiliation + authors
        3. Si hay aff_map, buscar coincidencias de instituciones
        4. Si tiene pycountry, buscar nombres de países en el texto
        5. Buscar también nombres oficiales y variantes (alt_spellings)
    
    Example:
        >>> row = pd.Series({'affiliation': 'Stanford University', 'authors': '...', 'country': ''})
        >>> aff_map = pd.DataFrame({'institution': ['Stanford'], 'country': ['USA']})
        >>> infer_country(row, aff_map)
        'USA'
    
    Notas:
        - Case-insensitive en todas las búsquedas
        - Requiere pycountry instalado para detección automática de países
        - Sin pycountry, solo funciona con mapeo manual
        - "Unknown" se usa para registros sin información geográfica
    """
    # === PASO 1: Prioridad al campo explícito ===
    if isinstance(row.get("country", ""), str) and row["country"]:
        return row["country"]
    
    # === PASO 2: Construir texto de búsqueda ===
    # Combina affiliation y authors para maximizar información
    aff_text = " ".join([
        str(row.get("affiliation", "")), 
        str(row.get("authors", ""))
    ]).lower()
    
    # === PASO 3: Buscar en mapeo manual (CSV externo) ===
    if aff_map is not None and not aff_map.empty:
        # Buscar coincidencia de institución en el texto
        for pat, country in zip(aff_map["institution"], aff_map["country"]):
            try:
                if pat.lower() in aff_text:
                    return country
            except Exception:
                pass
    
    # === PASO 4: Heurística con pycountry (detección automática) ===
    try:
        import pycountry  # type: ignore
        
        # Buscar nombres oficiales de países
        for c in pycountry.countries:
            # Nombre estándar
            if c.name.lower() in aff_text:
                return c.name
            
            # Nombres alternativos y variantes
            for n in getattr(c, "official_name", ""), *[a for a in getattr(c, "alt_spellings", [])]:
                if isinstance(n, str) and n and n.lower() in aff_text:
                    return c.name
    except Exception:
        # pycountry no disponible o error en búsqueda
        pass
    
    # === PASO 5: No se pudo determinar el país ===
    return "Unknown"

def compute_country_counts(df: pd.DataFrame, aff_map_csv: Optional[Path] = None) -> pd.DataFrame:
    """
    Calcula conteo de publicaciones por país del primer autor.
    
    Procesa el DataFrame completo de artículos para determinar la distribución
    geográfica de publicaciones basándose en el país del primer autor.
    
    Args:
        df (pd.DataFrame): DataFrame con artículos (columnas: authors, affiliation, country)
        aff_map_csv (Optional[Path]): Ruta a CSV con mapeo institution→country
                                      Formato: institution,country
    
    Returns:
        pd.DataFrame: DataFrame con columnas ['country', 'count']
                     Ordenado por count descendente
                     Excluye "Unknown"
    
    Proceso:
        1. Cargar mapeo manual si se proporciona CSV
        2. Extraer primer autor de cada publicación
        3. Inferir país para cada artículo
        4. Agrupar por país y contar publicaciones
        5. Filtrar "Unknown" y ordenar por count descendente
    
    Example:
        >>> df = load_bib_dataframe()
        >>> counts = compute_country_counts(df)
        >>> print(counts.head())
           country  count
        0      USA     45
        1    China     32
        2       UK     28
        ...
    
    Notas:
        - Solo considera el primer autor (asume afiliación principal)
        - Filtra registros con país "Unknown"
        - Útil para visualizar distribución geográfica de investigación
        - El mapeo CSV es opcional pero mejora precisión
    """
    # === PASO 1: Cargar mapeo manual si existe ===
    aff_map = None
    if aff_map_csv and Path(aff_map_csv).exists():
        aff_map = pd.read_csv(aff_map_csv)
    
    # === PASO 2: Extraer primer autor de cada publicación ===
    firsts = df["authors"].map(first_author)
    
    # === PASO 3: Inferir país para cada artículo ===
    countries = df.apply(lambda r: infer_country(r, aff_map), axis=1)
    
    # === PASO 4: Crear DataFrame con primer autor y país ===
    out = pd.DataFrame({"first_author": firsts, "country": countries})
    
    # === PASO 5: Agrupar y contar por país ===
    counts = out.groupby("country").size().reset_index(name="count")
    
    # Filtrar "Unknown" y ordenar por cantidad descendente
    counts = counts[counts["country"] != "Unknown"].sort_values("count", ascending=False)
    
    return counts

def plot_world_heatmap(counts: pd.DataFrame, out_png: Path, out_html: Path):
    """
    Genera mapa de calor mundial interactivo o gráfico de barras como alternativa.
    
    Intenta crear un mapa choropleth interactivo con Plotly. Si Plotly no está
    disponible o falla, genera un gráfico de barras con Matplotlib.
    
    Args:
        counts (pd.DataFrame): DataFrame con columnas ['country', 'count']
        out_png (Path): Ruta para guardar imagen PNG
        out_html (Path): Ruta para guardar HTML interactivo (solo con Plotly)
    
    Returns:
        bool: True si usó Plotly (mapa interactivo), False si usó Matplotlib (barras)
    
    Modo Plotly (preferido):
        - Mapa choropleth mundial interactivo
        - Colores en escala Blues según conteo
        - Hover muestra país y cantidad
        - Genera HTML interactivo + PNG estático (requiere kaleido)
    
    Modo Matplotlib (fallback):
        - Gráfico de barras horizontales
        - Todos los países visibles
        - Tamaño de figura adaptativo (min 16", +0.3" por país)
        - Solo PNG, no HTML
    
    Example:
        >>> counts = compute_country_counts(df)
        >>> is_plotly = plot_world_heatmap(counts, 
        ...                                Path("map.png"), 
        ...                                Path("map.html"))
        >>> print("Mapa interactivo" if is_plotly else "Gráfico de barras")
    
    Notas:
        - Plotly requiere: pip install plotly
        - PNG desde Plotly requiere: pip install kaleido
        - Sin kaleido, solo genera HTML
        - Matplotlib siempre genera PNG funcional
        - Usar locationmode="country names" requiere nombres estándar de países
    """
    try:
        # === INTENTO 1: Mapa interactivo con Plotly ===
        import plotly.express as px  # type: ignore
        
        # Convertir nombres de países a códigos ISO-3 para mejor mapeo
        counts_with_iso = counts.copy()
        try:
            import pycountry
            
            def extract_country_name(location_str: str) -> str:
                """
                Extrae el nombre del país de strings con formato 'Ciudad, País' o 'Ciudad, Estado, País'.
                
                Ejemplos:
                - "Kuala Lumpur, Malaysia" -> "Malaysia"
                - "Honolulu, HI, USA" -> "USA"
                - "Toronto ON, Canada" -> "Canada"
                - "France" -> "France"
                """
                # Dividir por coma y tomar el último elemento (asumiendo que es el país)
                parts = [p.strip() for p in location_str.split(',')]
                
                if len(parts) == 0:
                    return location_str
                
                # El país suele estar al final
                country_candidate = parts[-1]
                
                # Mapeo manual para casos especiales comunes
                country_mapping = {
                    'USA': 'United States',
                    'UK': 'United Kingdom',
                    'Turkiye': 'Turkey',
                    'Republic of Korea': 'South Korea',
                }
                
                return country_mapping.get(country_candidate, country_candidate)
            
            def get_iso3(country_name: str) -> str:
                """Convierte nombre de país a código ISO-3."""
                # Primero extraer el nombre real del país
                clean_country = extract_country_name(country_name)
                
                try:
                    country = pycountry.countries.search_fuzzy(clean_country)[0]
                    return country.alpha_3
                except (LookupError, AttributeError):
                    # Si falla, retornar el nombre limpio
                    return clean_country
            
            counts_with_iso["iso_alpha"] = counts_with_iso["country"].apply(get_iso3)
            counts_with_iso["country_clean"] = counts_with_iso["country"].apply(extract_country_name)
            
            # IMPORTANTE: Agrupar por ISO-3 para sumar todas las ciudades de cada país
            counts_with_iso = counts_with_iso.groupby("iso_alpha", as_index=False).agg({
                "count": "sum",
                "country_clean": "first"
            })
            
            location_col = "iso_alpha"
            location_mode = "ISO-3"
        except ImportError:
            # Si no hay pycountry, usar nombres directamente
            location_col = "country"
            location_mode = "country names"
        
        # Crear mapa choropleth mundial
        fig = px.choropleth(
            counts_with_iso, 
            locations=location_col, 
            locationmode=location_mode,  # Mapea por códigos ISO-3 o nombres
            color="count",
            hover_name="country_clean" if "country_clean" in counts_with_iso.columns else "country",  # Mostrar nombre limpio
            color_continuous_scale="Blues",  # Escala de azules
            title="Mapa de calor por país del primer autor"
        )
        
        # Mejorar visualización del mapa
        fig.update_geos(
            projection_type="natural earth",  # Proyección Natural Earth (más estética)
            showcoastlines=True,              # Mostrar líneas costeras
            coastlinecolor="RebeccaPurple",   # Color de las costas
            showland=True,                    # Mostrar tierra
            landcolor="white",                # Color de tierra sin datos
            showocean=True,                   # Mostrar océanos
            oceancolor="LightBlue",           # Color de océanos
            showcountries=True,               # Mostrar límites de países
            countrycolor="Black",             # Color de límites (negro para mejor definición)
            countrywidth=0.5,                 # Grosor de líneas de países
            showlakes=True,                   # Mostrar lagos
            lakecolor="LightBlue"             # Color de lagos
        )
        
        # Ajustar layout general
        fig.update_layout(
            margin=dict(l=0, r=0, t=60, b=0),
            height=600,                       # Altura del mapa
            title_font_size=20,               # Tamaño del título
            title_x=0.5                       # Centrar título
        )
        
        # Guardar HTML interactivo
        fig.write_html(str(out_html))
        
        # Intentar guardar PNG estático (requiere kaleido)
        png_generated = False
        try:
            fig.write_image(str(out_png), scale=2, width=1400, height=600)
            png_generated = True
            print(f"✓ PNG generado exitosamente con Kaleido: {out_png}")
        except Exception as e:
            print(f"⚠️ Error al generar PNG con Kaleido: {e}")
            print(f"   Generando PNG alternativo...")
            # Fallback: usar matplotlib para capturar el HTML
            try:
                import io
                from PIL import Image
                # Exportar como imagen usando el engine de plotly
                img_bytes = fig.to_image(format="png", width=1400, height=600, scale=2)
                with open(out_png, 'wb') as f:
                    f.write(img_bytes)
                png_generated = True
                print(f"✓ PNG generado con método alternativo: {out_png}")
            except Exception as e2:
                print(f"❌ No se pudo generar PNG: {e2}")
        
        if not png_generated:
            print(f"⚠️ Solo se generó HTML: {out_html}")
        
        return True  # Indica que se usó Plotly
        
    except Exception:
        # === FALLBACK: Gráfico de barras con Matplotlib ===
        import matplotlib.pyplot as plt
        
        # Copiar datos para visualización
        counts_plot = counts.copy()
        n_countries = len(counts_plot)
        
        # Ajustar tamaño de figura dinámicamente
        # Mínimo 16" de ancho, +0.3" por cada país
        fig_width = max(16, n_countries * 0.3)
        fig_height = 10
        
        # Crear gráfico de barras
        plt.figure(figsize=(fig_width, fig_height))
        plt.bar(range(n_countries), counts_plot["count"], color='steelblue')
        
        # Etiquetas de países en eje X
        plt.xticks(
            range(n_countries), 
            counts_plot["country"], 
            rotation=90,  # Vertical para legibilidad
            ha="center", 
            fontsize=8
        )
        
        # Etiquetas de ejes
        plt.xlabel("País", fontsize=11)
        plt.ylabel("Número de publicaciones", fontsize=11)
        plt.title(
            f"Primer autor por país (conteo) - {n_countries} países", 
            fontsize=13, 
            fontweight='bold'
        )
        
        # Grid para mejor lectura
        plt.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Ajustar layout y guardar
        plt.tight_layout()
        plt.savefig(out_png, dpi=200, bbox_inches='tight')
        plt.close()
        
        return False  # Indica que se usó Matplotlib
