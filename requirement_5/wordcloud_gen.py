"""
Módulo para generación de nubes de palabras (word clouds) bibliométricas.

Extrae texto de abstracts y keywords, lo preprocesa y genera visualizaciones
de frecuencia de términos como nubes de palabras.

Parte del Requerimiento 5: Visualizaciones avanzadas y reportes PDF.
"""
from __future__ import annotations
from pathlib import Path
import re
from typing import List
import pandas as pd
from requirement_2.preprocessing import Preprocessor

# Instancia global del preprocesador (tokenización, limpieza)
pp = Preprocessor()

def build_corpus(df: pd.DataFrame) -> str:
    """
    Construye corpus de texto concatenando abstracts y keywords de todos los registros.
    
    Proceso de 3 pasos:
    1. Itera por cada fila del DataFrame
    2. Extrae 'abstract' y 'keywords', concatena con espacio
    3. Une todos los textos en un único string
    
    Args:
        df (pd.DataFrame): DataFrame con columnas 'abstract' y/o 'keywords'
    
    Returns:
        str: Corpus completo con todos los textos concatenados
    
    Example:
        >>> df = pd.DataFrame({
        ...     'abstract': ['Machine learning algorithms', 'Neural networks'],
        ...     'keywords': ['AI, ML', 'Deep learning']
        ... })
        >>> corpus = build_corpus(df)
        >>> 'Machine learning' in corpus
        True
    
    Notas:
        - Convierte a string con str() para manejar valores None/NaN
        - get() con default "" evita KeyError si faltan columnas
        - Útil para análisis de frecuencia de términos
        - El corpus resultante será preprocesado antes de generar word cloud
    """
    texts = []
    
    # PASO 1-2: Extraer y concatenar abstract + keywords por registro
    for _, r in df.iterrows():
        chunk = " ".join([
            str(r.get("abstract", "")), 
            str(r.get("keywords", ""))
        ])
        texts.append(chunk)
    
    # PASO 3: Unir todo en un corpus único
    raw = " ".join(texts)
    return raw

def make_wordcloud(df: pd.DataFrame, out_png: Path, max_words: int = 150):
    """
    Genera nube de palabras a partir de abstracts y keywords del DataFrame.
    
    Proceso de 5 pasos:
    1. Construye corpus concatenando textos
    2. Tokeniza y limpia con Preprocessor
    3. Une tokens en texto limpio
    4. Genera word cloud con frecuencias
    5. Guarda imagen PNG
    
    Args:
        df (pd.DataFrame): DataFrame con columnas 'abstract', 'keywords'
        out_png (Path): Ruta para guardar imagen PNG
        max_words (int, optional): Número máximo de palabras a mostrar. Default: 150
    
    Returns:
        None: Guarda figura directamente en disco
    
    Example:
        >>> df = pd.DataFrame({
        ...     'abstract': ['machine learning for data analysis'] * 10,
        ...     'keywords': ['AI, ML, data science'] * 10
        ... })
        >>> make_wordcloud(df, Path("wordcloud.png"), max_words=50)
        # Genera nube con términos más frecuentes (learning, machine, data, ...)
    
    Características visuales:
        - Tamaño: 1400x800 píxeles
        - Fondo blanco
        - Tamaño de palabra proporcional a frecuencia
        - Hasta max_words términos más frecuentes
    
    Notas:
        - Requiere: pip install wordcloud
        - Preprocessor aplica: lowercase, stopwords, stemming (según configuración)
        - Palabras más frecuentes aparecen más grandes y centrales
        - Útil para identificar temas dominantes en corpus bibliométrico
    """
    from wordcloud import WordCloud
    
    # PASO 1: Construir corpus completo
    txt = build_corpus(df)
    
    # PASO 2-3: Tokenizar y limpiar texto
    cleaned = " ".join(pp.tokenize(txt))
    
    # PASO 4: Generar word cloud basado en frecuencias
    wc = WordCloud(
        width=1400, 
        height=800, 
        background_color="white", 
        max_words=max_words  # Limitar cantidad de términos
    ).generate(cleaned)
    
    # PASO 5: Guardar imagen
    wc.to_file(str(out_png))
