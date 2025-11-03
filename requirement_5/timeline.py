"""
Módulo para visualizaciones temporales de publicaciones bibliométricas.

Genera líneas de tiempo y series temporales que muestran:
- Evolución anual de publicaciones
- Distribución por revista a lo largo del tiempo
- Tendencias temporales en la producción científica

Parte del Requerimiento 5: Visualizaciones avanzadas y reportes PDF.
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

def to_int_year(s) -> int | None:
    """
    Convierte entrada a año entero válido o None.
    
    Extrae los primeros 4 caracteres, intenta convertir a entero y valida
    que esté en el rango [1900, 2100]. Si falla cualquier paso, retorna None.
    
    Args:
        s: Valor a convertir (str, int, float, etc.)
    
    Returns:
        int | None: Año válido o None si no cumple criterios
    
    Example:
        >>> to_int_year("2023")
        2023
        >>> to_int_year("2023-03-15")
        2023
        >>> to_int_year("1850")  # Fuera de rango
        None
        >>> to_int_year("invalid")
        None
    
    Notas:
        - Rango válido: 1900-2100 (cubre período bibliométrico relevante)
        - Solo usa primeros 4 caracteres para manejar formatos ISO (YYYY-MM-DD)
        - Maneja cualquier tipo de entrada mediante str()
    """
    try:
        # Extraer primeros 4 caracteres y convertir
        y = int(str(s)[:4])
        # Validar rango histórico razonable
        if 1900 <= y <= 2100: 
            return y
    except Exception:
        return None
    return None

def plot_year_series(df: pd.DataFrame, out_png: Path):
    """
    Genera gráfico de línea mostrando publicaciones por año.
    
    Proceso de 4 pasos:
    1. Convierte columna 'year' a enteros válidos
    2. Cuenta publicaciones por año
    3. Crea gráfico de línea con marcadores
    4. Guarda PNG con grid horizontal
    
    Args:
        df (pd.DataFrame): DataFrame con columna 'year'
        out_png (Path): Ruta para guardar imagen PNG
    
    Returns:
        None: Guarda figura directamente en disco
    
    Example:
        >>> df = pd.DataFrame({
        ...     'year': ['2020', '2021', '2021', '2022'],
        ...     'title': ['A', 'B', 'C', 'D']
        ... })
        >>> plot_year_series(df, Path("year_timeline.png"))
        # Genera: 2020(1), 2021(2), 2022(1)
    
    Características visuales:
        - Figura 12x5"
        - Línea con marcadores circulares
        - Grid horizontal para lectura
        - DPI 220 para alta calidad
    
    Notas:
        - Años inválidos son ignorados (dropna)
        - Ordenado cronológicamente (sort_index)
        - Útil para detectar gaps o tendencias temporales
    """
    # PASO 1: Convertir y limpiar años
    years = df["year"].map(to_int_year).dropna().astype(int)
    
    # PASO 2: Contar publicaciones por año
    ser = years.value_counts().sort_index()
    
    # PASO 3: Crear gráfico de línea
    plt.figure(figsize=(12, 5))
    plt.plot(ser.index, ser.values, marker="o")
    plt.title("Publicaciones por año")
    plt.xlabel("Año")
    plt.ylabel("Cantidad")
    plt.grid(True, axis="y", alpha=0.3)
    
    # PASO 4: Guardar imagen
    plt.tight_layout()
    plt.savefig(out_png, dpi=220)

def plot_journal_series(df: pd.DataFrame, out_png: Path, top_n: int = 8):
    """
    Genera gráfico de área apilada mostrando publicaciones por año y revista.
    
    Proceso de 7 pasos:
    1. Convierte años a enteros válidos
    2. Elimina registros sin año
    3. Identifica top N revistas más frecuentes
    4. Agrupa revistas restantes en "Otros"
    5. Crea tabla pivot (año x revista)
    6. Genera gráfico de área apilada
    7. Guarda PNG con leyenda externa
    
    Args:
        df (pd.DataFrame): DataFrame con columnas 'year', 'journal', 'title'
        out_png (Path): Ruta para guardar imagen PNG
        top_n (int, optional): Número de revistas principales a mostrar. Default: 8
    
    Returns:
        None: Guarda figura directamente en disco
    
    Example:
        >>> df = pd.DataFrame({
        ...     'year': ['2020', '2020', '2021', '2021'],
        ...     'journal': ['Nature', 'Science', 'Nature', 'Cell'],
        ...     'title': ['A', 'B', 'C', 'D']
        ... })
        >>> plot_journal_series(df, Path("journal_timeline.png"), top_n=2)
        # Muestra Nature(2), Science(1), Otros[Cell](1)
    
    Características visuales:
        - Figura 14x6" para acomodar leyenda
        - Áreas apiladas con colores diferenciados
        - Leyenda externa (derecha) para no obstruir
        - DPI 220, bbox_inches='tight' para incluir leyenda
    
    Notas:
        - Revistas fuera del top_n se agrupan en "Otros"
        - Útil para identificar revistas dominantes por período
        - pivot_table cuenta títulos (aggfunc="count")
        - fillna(0) maneja años sin publicaciones en cierta revista
    """
    # PASO 1-2: Preparar datos temporales
    tmp = df.copy()
    tmp["year"] = tmp["year"].map(to_int_year)
    tmp = tmp.dropna(subset=["year"])
    tmp["year"] = tmp["year"].astype(int)
    
    # PASO 3: Identificar revistas más frecuentes
    top = tmp["journal"].value_counts().head(top_n).index.tolist()
    
    # PASO 4: Agrupar revistas no-top en "Otros"
    tmp["journal_top"] = tmp["journal"].where(tmp["journal"].isin(top), "Otros")
    
    # PASO 5: Crear tabla pivot (año x revista)
    piv = tmp.pivot_table(
        index="year", 
        columns="journal_top", 
        values="title", 
        aggfunc="count"  # Contar publicaciones
    ).fillna(0)
    
    # PASO 6: Generar gráfico de área apilada
    fig, ax = plt.subplots(figsize=(14, 6))
    piv.plot(kind="area", stacked=True, ax=ax)
    ax.set_title("Publicaciones por año y revista (Top {})".format(top_n))
    ax.set_xlabel("Año")
    ax.set_ylabel("Cantidad")
    
    # Leyenda externa (derecha) para no obstruir gráfico
    ax.legend(
        loc='center left', 
        bbox_to_anchor=(1.02, 0.5),  # Posición: fuera del eje
        fontsize=8, 
        frameon=True, 
        framealpha=0.9
    )
    
    # PASO 7: Guardar con leyenda incluida
    plt.tight_layout()
    plt.savefig(out_png, dpi=220, bbox_inches='tight')
    plt.close()
