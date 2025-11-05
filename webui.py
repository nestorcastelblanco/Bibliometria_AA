from __future__ import annotations
from flask import Flask, render_template, request, jsonify, send_from_directory
import subprocess, os, sys, shutil, hashlib
from pathlib import Path
import csv
from typing import List, Dict

# Force reload - Updated geo.py with ISO-3 country mapping
APP_ROOT = Path(__file__).resolve().parent
DATA = APP_ROOT / "data" / "processed"
STAGE = DATA / "_mirror"
STAGE.mkdir(parents=True, exist_ok=True)

# Directorios base (globales) donde podríamos encontrar salidas
GLOBAL_SEARCH_DIRS = [
    DATA,
    APP_ROOT / "requirement_1",
    APP_ROOT / "requirement_2",
    APP_ROOT / "requirement_3",
    APP_ROOT / "requirement_4",
    APP_ROOT / "requirement_5",
    APP_ROOT / "requirement_grafos",
    APP_ROOT / "Seguimiento_1",
    APP_ROOT / "plots",
    APP_ROOT / "figures",
    APP_ROOT / "output",
    APP_ROOT / "outputs",
    APP_ROOT / "data",
]

IMG_EXTS = {".png", ".jpg", ".jpeg", ".svg", ".gif", ".webp"}
PDF_EXTS = {".pdf"}

# Forzar UTF-8 para este proceso
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass
os.environ.setdefault("PYTHONIOENCODING","utf-8")
os.environ.setdefault("PYTHONUTF8","1")

PY = sys.executable  # venv python

def run_py_utf8(args: list[str]) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    cmd = [PY, "-X", "utf8"] + args
    return subprocess.run(cmd, check=True, env=env, capture_output=True, text=True)

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

# ---------- Servir archivos desde data/processed ----------
@app.get("/files/<path:filename>")
def files(filename: str):
    safe = os.path.normpath(filename).replace("\\", "/")
    return send_from_directory(DATA, safe)

def _hash_path(p: Path) -> str:
    return hashlib.sha1(str(p.resolve()).encode("utf-8")).hexdigest()[:12]

def _stage_into_processed(p: Path) -> Path | None:
    """
    Si p está fuera de DATA: copiar a _mirror con nombre estable (hash__name.ext)
    y devolver ruta relativa a DATA. Si ya está en DATA, devolver su ruta relativa.
    """
    try:
        p = p.resolve()
    except Exception:
        p = Path(p)

    try:
        # ya está dentro de DATA
        rel = p.relative_to(DATA)
        return rel
    except Exception:
        pass

    if not p.exists() or not p.is_file():
        return None

    h = _hash_path(p)
    dst = STAGE / f"{h}__{p.name}"
    try:
        copy = True
        if dst.exists():
            s, d = p.stat(), dst.stat()
            if s.st_size == d.st_size and int(s.st_mtime) <= int(d.st_mtime):
                copy = False
        if copy:
            shutil.copy2(p, dst)
        return dst.relative_to(DATA)
    except Exception:
        return None

# ---------- Alcances (scopes) por requerimiento ----------
def _scope_map() -> Dict[str, Dict[str, list]]:
    """
    Define para cada scope:
      - dirs: lista de carpetas donde buscar
      - glob_images: patrones glob (lista) de imágenes
      - glob_pdfs: patrones glob (lista) de PDFs
    """
    return {
        "req1": {
            "dirs": [DATA, APP_ROOT/"requirement_1", APP_ROOT/"Seguimiento_1"],
            "glob_images": ["req1*.*", "*unificar*.*", "*acm*.*", "*sage*.*", "*automat*.*"],
            "glob_pdfs":   ["req1*.pdf", "*reporte*.pdf", "*unificar*.pdf"],
        },
        "req2": {
            "dirs": [DATA, APP_ROOT/"requirement_2"],
            "glob_images": ["req2*.*", "similitud*.*", "similarity*.*", "pairs*.*", "result*.*"],
            "glob_pdfs":   ["reporte_similitud*.pdf", "req2*.pdf", "*similitud*.pdf"],
        },
        "req3": {
            "dirs": [DATA, APP_ROOT/"requirement_3"],
            "glob_images": ["req3*.*", "freq*.*", "frecuen*.*", "wordcloud*.*", "nube*.*", "*precision*.*"],
            "glob_pdfs":   ["req3*.pdf", "*frecuencia*.pdf", "*wordcloud*.pdf"],
        },
        "req4": {
            "dirs": [DATA, APP_ROOT/"requirement_4"],
            "glob_images": ["req4*.*", "dendro*.*", "cluster*.*", "linkage*.*"],
            "glob_pdfs":   ["req4*.pdf", "*dendro*.pdf", "*cluster*.pdf"],
        },
        "req5": {
            "dirs": [DATA, APP_ROOT/"requirement_5"],
            "glob_images": ["req5*.*", "heatmap*.*", "timeline*.*", "wordcloud*.*", "mapa*.*"],
            "glob_pdfs":   ["req5*.pdf", "*heatmap*.pdf", "*timeline*.pdf", "*wordcloud*.pdf"],
        },
        "grafos_cit": {
            "dirs": [DATA, APP_ROOT/"requirement_grafos"],
            "glob_images": ["cit*.*", "cita*.*", "graph*cit*.*", "grafos*cit*.*", "*scc*.*", "*dijkstra*.*", "*fw*.*"],
            "glob_pdfs":   ["*grafos*cit*.pdf", "*citaciones*.pdf"],
        },
        "grafos_terms": {
            "dirs": [DATA, APP_ROOT/"requirement_grafos"],
            "glob_images": ["term*.*", "cooc*.*", "grafos*term*.*", "graph*term*.*", "*degree*.*", "*component*.*"],
            "glob_pdfs":   ["*grafos*term*.pdf", "*terminos*.pdf", "*cooc*.pdf"],
        },
    }

def _iter_files(dirs: List[Path], patterns: List[str], exts: set[str]) -> List[Path]:
    out = []
    for root in dirs:
        if not root.exists():
            continue
        for pat in (patterns or ["*"]):
            for p in root.rglob(pat):
                if p.is_file() and p.suffix.lower() in exts:
                    out.append(p)
    return out

def _list_assets_by_scope(scope: str, limit: int = 24) -> Dict[str, list]:
    """
    Busca imágenes y PDFs solo del scope indicado. Estagia archivos fuera de DATA.
    Retorna rutas relativas a DATA para servir con /files/...
    """
    conf = _scope_map().get(scope)
    if not conf:
        # Fallback: lista global
        conf = {"dirs": GLOBAL_SEARCH_DIRS, "glob_images": ["*"], "glob_pdfs": ["*"]}

    imgs = _iter_files(conf["dirs"], conf.get("glob_images", ["*"]), IMG_EXTS)
    pdfs = _iter_files(conf["dirs"], conf.get("glob_pdfs", ["*"]), PDF_EXTS)

    # Ordenar por mtime reciente
    imgs.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    pdfs.sort(key=lambda p: p.stat().st_mtime, reverse=True)

    def stage_many(paths: List[Path], lim: int, want: str) -> List[dict]:
        items = []
        for p in paths[:lim]:
            rel = _stage_into_processed(p)
            if not rel:
                continue
            abs_in_data = DATA / rel
            try:
                st = abs_in_data.stat()
                items.append({
                    "rel": rel.as_posix(),
                    "name": abs_in_data.name,
                    "bytes": st.st_size,
                    "mtime": st.st_mtime,
                    "type": want
                })
            except Exception:
                continue
        return items

    return {
        "images": stage_many(imgs, limit, "image"),
        "pdfs":   stage_many(pdfs, limit, "pdf"),
    }

# ---------- API de assets por scope ----------
@app.get("/api/list_assets")
def api_list_assets():
    scope = (request.args.get("scope") or "").strip().lower()
    try:
        limit = int(request.args.get("limit", "24"))
    except:
        limit = 24
    assets = _list_assets_by_scope(scope, limit=limit)
    return jsonify({"ok": True, "scope": scope, "items": assets})

# ---------- Endpoints de ejecución ----------
@app.post("/api/req1")
def api_req1():
    payload = request.get_json(force=True, silent=True) or {}
    _ = (payload.get("query") or "").strip()
    try:
        out = run_py_utf8(["main.py", "req1"])
        return jsonify({"ok": True, "stdout": out.stdout, "stderr": out.stderr})
    except subprocess.CalledProcessError as e:
        return jsonify({"ok": False, "stdout": e.stdout, "stderr": e.stderr}), 500

@app.post("/api/req2")
def api_req2():
    payload = request.get_json(force=True, silent=True) or {}
    indices = payload.get("indices") or []
    if not indices or len(indices) < 2:
        return jsonify({"ok": False, "error": "Debes enviar al menos 2 índices"}), 400
    try:
        out = run_py_utf8(["main.py", "req2", *[str(i) for i in indices]])
        # cargar CSV TOP si existe
        csv_path = DATA / "reporte_similitud_top.csv"
        rows = []
        if csv_path.exists():
            with open(csv_path, "r", encoding="utf-8", newline="") as f:
                rows = list(csv.DictReader(f))
        md_path = DATA / "reporte_similitud.md"
        md_text = md_path.read_text(encoding="utf-8") if md_path.exists() else ""
        return jsonify({"ok": True, "stdout": out.stdout, "table": rows, "md": md_text})
    except subprocess.CalledProcessError as e:
        return jsonify({"ok": False, "stdout": e.stdout, "stderr": e.stderr}), 500

@app.post("/api/req3")
def api_req3():
    try:
        out = run_py_utf8(["main.py", "req3"])
        json_path = APP_ROOT / "requirement_3" / "req3_resultados.json"
        js = {}
        if json_path.exists():
            import json
            js = json.loads(json_path.read_text(encoding="utf-8"))
        return jsonify({"ok": True, "stdout": out.stdout, "result": js})
    except subprocess.CalledProcessError as e:
        return jsonify({"ok": False, "stdout": e.stdout, "stderr": e.stderr}), 500

@app.post("/api/req4")
def api_req4():
    try:
        out = run_py_utf8(["main.py", "req4"])
        return jsonify({"ok": True, "stdout": out.stdout})
    except subprocess.CalledProcessError as e:
        return jsonify({"ok": False, "stdout": e.stdout, "stderr": e.stderr}), 500

@app.post("/api/req5")
def api_req5():
    try:
        out = run_py_utf8(["main.py", "req5"])
        return jsonify({"ok": True, "stdout": out.stdout})
    except subprocess.CalledProcessError as e:
        return jsonify({"ok": False, "stdout": e.stdout, "stderr": e.stderr}), 500

@app.post("/api/grafos/cit")
def api_grafos_cit():
    try:
        out = run_py_utf8(["main.py", "grafos_cit"])
        return jsonify({"ok": True, "stdout": out.stdout})
    except subprocess.CalledProcessError as e:
        return jsonify({"ok": False, "stdout": e.stdout, "stderr": e.stderr}), 500

@app.post("/api/grafos/terms")
def api_grafos_terms():
    try:
        out = run_py_utf8(["main.py", "grafos_terms"])
        return jsonify({"ok": True, "stdout": out.stdout})
    except subprocess.CalledProcessError as e:
        return jsonify({"ok": False, "stdout": e.stdout, "stderr": e.stderr}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=7860, debug=True)
