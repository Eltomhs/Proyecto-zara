# zara/views.py
from __future__ import annotations

from typing import Tuple, List, Dict, Optional
import pandas as pd
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET
from django.contrib.staticfiles import finders  # localizar archivos 

# VISTAS HTML

def home(request: HttpRequest) -> HttpResponse:
    return render(request, "encuesta_zara/home.html")

def tradein(request: HttpRequest) -> HttpResponse:
    return render(request, "encuesta_zara/tradein.html")

def gracias(request: HttpRequest) -> HttpResponse:
    return render(request, "encuesta_zara/gracias.html")

def informe_encuesta(request: HttpRequest) -> HttpResponse:
    return render(request, "encuesta_zara/informe.html")


# LECTURA CSV DESDE STATIC/

STATIC_CSV_CANDIDATES = [
    "data/respuestas.csv",         
    "zara/data/respuestas.csv",
    "zara/respuestas.csv",
]

def _csv_absolute_path() -> str:
    for rel in STATIC_CSV_CANDIDATES:
        abs_path = finders.find(rel)
        if abs_path:
            return abs_path
    raise FileNotFoundError(
        "No se encontró 'respuestas.csv' en static/. Probé: " + ", ".join(STATIC_CSV_CANDIDATES)
    )

def _load_df() -> pd.DataFrame:
    csv_path = _csv_absolute_path()
    df = pd.read_csv(csv_path, encoding="utf-8-sig")
    # limpiar
    df.columns = [c.strip() for c in df.columns]
    for c in df.columns:
        if df[c].dtype == object:
            df[c] = df[c].astype(str).str.strip()
    # normaliza edad
    if "¿En qué rango de edad se encuentra? " in df.columns:
        df["¿En qué rango de edad se encuentra? "] = df["¿En qué rango de edad se encuentra? "].str.replace("–", "-", regex=False)
    # normaliza importancia 
    imp_col = "En una escala de 1 a 5, ¿qué tan importante es para usted la sostenibilidad al comprar ropa? "
    if imp_col in df.columns:
        df[imp_col] = df[imp_col].astype(str).str.extract(r"(\d)").astype(float)
    return df


COL: Dict[str, str] = {
    "ts": "Timestamp",
    "oiste": "¿Has escuchado el término fast fashion?",
    "asocia": "¿Asocias a Zara con fast fashion?",
    "factor": "¿Qué factor influye más en su decisión de compra de ropa?",
    "canal": "¿Dónde suele comprar en Zara?",
    "importancia": "En una escala de 1 a 5, ¿qué tan importante es para usted la sostenibilidad al comprar ropa?",
    "compraria": "Si Zara ofreciera ropa más sostenible con un precio ligeramente mayor, ¿la compraría?",
    "info": "¿Qué información le gustaría encontrar en la web de Zara para decidir de forma más sostenible?",
    "futuro": "¿En qué aspecto debería enfocarse más Zara en el futuro?",
    "edad": "¿En qué rango de edad se encuentra?",
    "genero": "¿Cuál es su género?",
}



YES_WORDS = {"si", "sí", "yes", "y"}
NO_WORDS  = {"no", "n"}

# HELPERS  

def _series(df: pd.DataFrame, key: str) -> pd.Series:
    return df.get(COL[key], pd.Series(dtype=object))

def _yes_no_counts(series: pd.Series) -> Tuple[int, int]:
    yes = 0; no = 0
    for v in series.fillna(""):
        s = str(v).strip().lower()
        if s in YES_WORDS: yes += 1
        elif s in NO_WORDS or s == "no estoy seguro/a": no += 1
        elif s != "": no += 1
    return int(yes), int(no)

def _cat_counts(series: pd.Series) -> Tuple[List[str], List[int]]:
    vc = series.dropna().astype(str).str.strip()
    vc = vc[vc != ""]
    counts = vc.value_counts()
    labels = counts.index.tolist()
    data = [int(x) for x in counts.values.tolist()]
    return labels, data

def _likert_counts(series: pd.Series) -> Tuple[List[str], List[int], Optional[float]]:
    s = pd.to_numeric(series, errors="coerce").dropna().astype(int)
    labels = ["1", "2", "3", "4", "5"]
    data = [int((s == i).sum()) for i in range(1, 6)] 
    avg = float(round(float(s.mean()), 2)) if len(s) else None
    return labels, data, avg

def _multi_counts(series: pd.Series) -> Tuple[List[str], List[int]]:
    counts: Dict[str, int] = {}
    for v in series.dropna():
        for item in [x.strip() for x in str(v).split(",")]:
            if not item:
                continue
            counts[item] = counts.get(item, 0) + 1
    labels = list(counts.keys())
    data = [int(x) for x in counts.values()]
    return labels, data



@require_GET
def encuesta_json(request: HttpRequest) -> JsonResponse:
    try:
        df = _load_df()
    except Exception as e:
        return JsonResponse({"error": f"No se pudo leer el CSV: {e}"}, status=500)

    total = int(len(df))

    conoce_yes, conoce_no = _yes_no_counts(_series(df, "oiste"))
    asocia_yes, asocia_no = _yes_no_counts(_series(df, "asocia"))

    canal_labels,  canal_data  = _cat_counts(_series(df, "canal"))
    factor_labels, factor_data = _cat_counts(_series(df, "factor"))
    pagar_labels,  pagar_data  = _cat_counts(_series(df, "compraria"))
    edad_labels,   edad_data   = _cat_counts(_series(df, "edad"))
    genero_labels, genero_data = _cat_counts(_series(df, "genero"))

    lik_labels, lik_data, lik_avg = _likert_counts(_series(df, "importancia"))
    info_labels, info_data = _multi_counts(_series(df, "info"))

    resp: Dict[str, object] = {
        "kpis": {
            "total_respuestas": total,
            "pct_conoce": round((conoce_yes / total) * 100, 1) if total else None,
            "pct_asocia": round((asocia_yes / total) * 100, 1) if total else None,
            "promedio_importancia": lik_avg if lik_avg is None else float(lik_avg),
        },
        "charts": {
            "conoce": {"labels": ["Sí", "No / No seguro"], "data": [conoce_yes, conoce_no]},
            "asocia": {"labels": ["Sí", "No / No seguro"], "data": [asocia_yes, asocia_no]},
            "canal":  {"labels": canal_labels,  "data": canal_data},
            "factor": {"labels": factor_labels, "data": factor_data},
            "likert": {"labels": lik_labels,   "data": lik_data, "promedio": lik_avg},
            "pagar":  {"labels": pagar_labels, "data": pagar_data},
            "info":   {"labels": info_labels,  "data": info_data},
            "edad":   {"labels": edad_labels,  "data": edad_data},
            "genero": {"labels": genero_labels,"data": genero_data},
        },
    }
    return JsonResponse(resp, json_dumps_params={"ensure_ascii": False})
