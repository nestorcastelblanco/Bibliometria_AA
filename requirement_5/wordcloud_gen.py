from __future__ import annotations
from pathlib import Path
import re
from typing import List
import pandas as pd
from requirement_2.preprocessing import Preprocessor

pp = Preprocessor()

def build_corpus(df: pd.DataFrame) -> str:
    texts = []
    for _, r in df.iterrows():
        chunk = " ".join([str(r.get("abstract","")), str(r.get("keywords",""))])
        texts.append(chunk)
    raw = " ".join(texts)
    return raw

def make_wordcloud(df: pd.DataFrame, out_png: Path, max_words: int = 150):
    from wordcloud import WordCloud
    txt = build_corpus(df)
    cleaned = " ".join(pp.tokenize(txt))
    wc = WordCloud(width=1400, height=800, background_color="white", max_words=max_words).generate(cleaned)
    wc.to_file(str(out_png))
