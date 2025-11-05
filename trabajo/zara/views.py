from __future__ import annotations

from typing import Tuple, List, Dict, Optional
from functools import lru_cache
import json
from datetime import datetime
import pandas as pd
from django.http import HttpRequest, HttpResponse, Http404, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.contrib.staticfiles import finders


# =============================
#  PÁGINAS BÁSICAS / CATÁLOGO
# =============================

def home(request: HttpRequest) -> HttpResponse:
    return render(request, "encuesta_zara/home.html")

def invitado(request: HttpRequest) -> HttpResponse:
    return render(request, "encuesta_zara/invitado.html")

def mujer(request: HttpRequest) -> HttpResponse:
    return render(request, "encuesta_zara/mujer.html")

def hombre(request: HttpRequest) -> HttpResponse:
    return render(request, "encuesta_zara/hombre.html")

def nina(request: HttpRequest) -> HttpResponse:
    # Archivo sin tilde en el nombre del template: "nina.html"
    return render(request, "encuesta_zara/nina.html")

def nino(request: HttpRequest) -> HttpResponse:
    # Archivo sin tilde en el nombre del template: "nino.html"
    return render(request, "encuesta_zara/nino.html")

def accesorios(request: HttpRequest) -> HttpResponse:
    return render(request, "encuesta_zara/accesorios.html")

def perfume(request: HttpRequest) -> HttpResponse:
    # Asegúrate de tener "perfumes.html" en templates/encuesta_zara/
    return render(request, "encuesta_zara/perfumes.html")

def tradein(request: HttpRequest) -> HttpResponse:
    return render(request, "encuesta_zara/tradein.html")


# =============================
#  CARRITO DE COMPRAS (LOCALSTORAGE)
# =============================

def carrito(request: HttpRequest) -> HttpResponse:
    """
    Página del carrito. No usa DB: el contenido se renderiza en el cliente
    leyendo localStorage ('zara_cart'). Esta vista solo entrega el HTML.
    """
    return render(request, "encuesta_zara/carrito.html")


# =============================
#  CARGA CSV DESDE static/
# =============================

# Posibles ubicaciones del CSV dentro de static/ (ajusta si cambiaste estructura)
STATIC_CSV_CANDIDATES = [
    "data/respuestas.csv",
    "zara/data/respuestas.csv",
    "zara/respuestas.csv",
    "encuesta_zara/data/respuestas.csv",
]

def _csv_absolute_path() -> str:
    """
    Busca el CSV en static/ usando el collector de Django.
    Lanza FileNotFoundError si no lo encuentra.
    """
    for rel in STATIC_CSV_CANDIDATES:
        abs_path = finders.find(rel)
        if abs_path:
            return abs_path
    raise FileNotFoundError(
        "No se encontró 'respuestas.csv' en static/. Probé: " + ", ".join(STATIC_CSV_CANDIDATES)
    )

@lru_cache(maxsize=1)
def _load_df() -> pd.DataFrame:
    """
    Carga el CSV y aplica limpieza básica.
    Si no existe o hay error, retorna DataFrame vacío para no romper el dashboard.
    """
    try:
        csv_path = _csv_absolute_path()
        df = pd.read_csv(csv_path, encoding="utf-8-sig")
    except Exception:
        return pd.DataFrame()

    # Limpieza básica
    df.columns = [c.strip() for c in df.columns]
    for c in df.columns:
        if df[c].dtype == object:
            df[c] = df[c].astype(str).str.strip()

    # Normalización de guión en rangos de edad
    for ec in ["¿En qué rango de edad se encuentra? ", "¿En qué rango de edad se encuentra?"]:
        if ec in df.columns:
            df[ec] = df[ec].str.replace("–", "-", regex=False)

    # Likert (1-5): extrae dígito si viene con texto
    for ic in [
        "En una escala de 1 a 5, ¿qué tan importante es para usted la sostenibilidad al comprar ropa? ",
        "En una escala de 1 a 5, ¿qué tan importante es para usted la sostenibilidad al comprar ropa?",
    ]:
        if ic in df.columns:
            df[ic] = df[ic].astype(str).str.extract(r"(\d)").astype(float)

    return df


# =============================
#  MAPEO Y HELPERS DE ANÁLISIS
# =============================

COL: Dict[str, str] = {
    "ts":         "Timestamp",
    "oiste":      "¿Has escuchado el término fast fashion?",
    "asocia":     "¿Asocias a Zara con fast fashion?",
    "factor":     "¿Qué factor influye más en su decisión de compra de ropa?",
    "canal":      "¿Dónde suele comprar en Zara?",
    "importancia":"En una escala de 1 a 5, ¿qué tan importante es para usted la sostenibilidad al comprar ropa?",
    "compraria":  "Si Zara ofreciera ropa más sostenible con un precio ligeramente mayor, ¿la compraría?",
    "info":       "¿Qué información le gustaría encontrar en la web de Zara para decidir de forma más sostenible?",
    "futuro":     "¿En qué aspecto debería enfocarse más Zara en el futuro?",
    "edad":       "¿En qué rango de edad se encuentra?",
    "genero":     "¿Cuál es su género?",
}

YES_WORDS = {"si", "sí", "yes", "y"}
NO_WORDS  = {"no", "n", "no estoy seguro/a", "no estoy seguro", "no seguro"}

def _series(df: pd.DataFrame, key: str) -> pd.Series:
    col = COL.get(key)
    if not col or df.empty or col not in df.columns:
        return pd.Series([], dtype=object)
    return df[col]

def _yes_no_counts(series: pd.Series) -> Tuple[int, int]:
    yes = 0
    no = 0
    for v in series.fillna(""):
        s = str(v).strip().lower()
        if s in YES_WORDS:
            yes += 1
        elif s in NO_WORDS or s != "":
            # Todo lo que no es 'sí' y no está vacío => 'No / No seguro'
            no += 1
    return int(yes), int(no)

def _cat_counts(series: pd.Series) -> Tuple[List[str], List[int]]:
    if series.empty:
        return [], []
    vc = series.dropna().astype(str).str.strip()
    vc = vc[vc != ""]
    if vc.empty:
        return [], []
    counts = vc.value_counts()
    return counts.index.tolist(), [int(x) for x in counts.values.tolist()]

def _likert_counts(series: pd.Series) -> Tuple[List[str], List[int], Optional[float]]:
    labels = ["1", "2", "3", "4", "5"]
    if series.empty:
        return labels, [0, 0, 0, 0, 0], None
    s = pd.to_numeric(series, errors="coerce").dropna().astype(int)
    data = [int((s == i).sum()) for i in range(1, 6)]
    avg = float(round(float(s.mean()), 2)) if len(s) else None
    return labels, data, avg

def _multi_counts(series: pd.Series) -> Tuple[List[str], List[int]]:
    if series.empty:
        return [], []
    counts: Dict[str, int] = {}
    for v in series.dropna():
        for item in [x.strip() for x in str(v).split(",")]:
            if not item:
                continue
            counts[item] = counts.get(item, 0) + 1
    return list(counts.keys()), [int(x) for x in counts.values()]


# =============================
#  DASHBOARD Y DETALLE
# =============================

def _empty_payload() -> Dict[str, Dict[str, object]]:
    charts = {
        "conoce": {"type": "doughnut", "labels": ["Sí", "No / No seguro"], "data": [0, 0]},
        "asocia": {"type": "doughnut", "labels": ["Sí", "No / No seguro"], "data": [0, 0]},
        "canal":  {"type": "bar",      "labels": [], "data": []},
        "factor": {"type": "bar",      "labels": [], "data": []},
        "likert": {"type": "bar",      "labels": ["1","2","3","4","5"], "data": [0,0,0,0,0], "avg": None},
        "pagar":  {"type": "doughnut", "labels": [], "data": []},
        "info":   {"type": "bar",      "labels": [], "data": []},
        "edad":   {"type": "bar",      "labels": [], "data": []},
        "genero": {"type": "pie",      "labels": [], "data": []},
    }
    kpis = {
        "total_respuestas": 0,
        "pct_conoce": None,
        "pct_asocia": None,
        "promedio_importancia": None,
    }
    return {"kpis": kpis, "charts": charts}

def _build_all_datasets(df: pd.DataFrame) -> Dict[str, Dict[str, object]]:
    if df is None or df.empty:
        return _empty_payload()

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

    charts = {
        "conoce": {"type": "doughnut", "labels": ["Sí", "No / No seguro"], "data": [conoce_yes, conoce_no]},
        "asocia": {"type": "doughnut", "labels": ["Sí", "No / No seguro"], "data": [asocia_yes, asocia_no]},
        "canal":  {"type": "bar",      "labels": canal_labels,  "data": canal_data},
        "factor": {"type": "bar",      "labels": factor_labels, "data": factor_data},
        "likert": {"type": "bar",      "labels": lik_labels,    "data": lik_data, "avg": lik_avg},
        "pagar":  {"type": "doughnut", "labels": pagar_labels,  "data": pagar_data},
        "info":   {"type": "bar",      "labels": info_labels,   "data": info_data},
        "edad":   {"type": "bar",      "labels": edad_labels,   "data": edad_data},
        "genero": {"type": "pie",      "labels": genero_labels, "data": genero_data},
    }

    kpis = {
        "total_respuestas": total,
        "pct_conoce": round((conoce_yes / total) * 100, 1) if total else None,
        "pct_asocia": round((asocia_yes / total) * 100, 1) if total else None,
        "promedio_importancia": lik_avg if lik_avg is None else float(lik_avg),
    }

    return {"kpis": kpis, "charts": charts}


def informe_encuesta(request: HttpRequest) -> HttpResponse:
    """
    Dashboard principal: datasets listos en el context.
    Si no hay CSV, renderiza todo con ceros/None y muestra aviso en plantilla.
    """
    df = _load_df()
    payload = _build_all_datasets(df)
    payload["csv_ok"] = not df.empty
    return render(request, "encuesta_zara/informe.html", payload)


CHART_TITLES: Dict[str, str] = {
    "conoce": "¿Ha escuchado el término “Fast Fashion”?",
    "asocia": "¿Asocia a Zara con Fast Fashion?",
    "canal":  "¿Dónde suele comprar en Zara?",
    "likert": "Importancia de la sostenibilidad (1–5)",
    "pagar":  "¿Pagaría más si fuera sostenible?",
    "factor": "Factor que más influye en la compra",
    "info":   "Información de sostenibilidad que desean ver",
    "edad":   "Distribución por rango de edad",
    "genero": "Distribución por género",
}

def chart_detail(request: HttpRequest, key: str) -> HttpResponse:
    """
    Página de detalle para un gráfico específico del dashboard.
    """
    if key not in CHART_TITLES:
        raise Http404("Gráfico no encontrado")

    df = _load_df()
    payload = _build_all_datasets(df)
    chart = payload["charts"].get(key)
    if not chart:
        raise Http404("Serie no disponible")

    context = {
        "key": key,
        "title": CHART_TITLES[key],
        "chart": chart,          # {type, labels, data, (avg)}
        "kpis": payload["kpis"], # KPIs para cabecera
        "csv_ok": not df.empty,
    }
    return render(request, "encuesta_zara/chart_detail.html", context)


# =============================
#  APIs PARA REGLAS DE NEGOCIO (LOCALSTORAGE)
# =============================

# Config de reglas de carrito (sin DB)
MAX_QTY_PER_ITEM = 10

# Ejemplos de cupones; puedes moverlos a settings o DB después
CUPONES: Dict[str, Dict[str, object]] = {
    "ECO10": {
        "percent": 10,
        "desde": datetime(2025, 1, 1, 0, 0, 0),
        "hasta": datetime(2025, 12, 31, 23, 59, 59),
        "activo": True,
    },
    "GREEN20": {
        "percent": 20,
        "desde": datetime(2025, 11, 1, 0, 0, 0),
        "hasta": datetime(2025, 11, 30, 23, 59, 59),
        "activo": True,
    },
}

# Simulación de stock por SKU (si aún no tienes modelos)
STOCK: Dict[str, int] = {
    "SKU-001": 5,
    "SKU-002": 20,
    "SKU-003": 2,
}

def _json_body(request: HttpRequest) -> Dict[str, object]:
    try:
        return json.loads(request.body.decode("utf-8"))
    except Exception:
        return {}

def _cupon_vigente(data: Dict[str, object]) -> bool:
    now = datetime.now()
    return bool(data.get("activo")) and data.get("desde") <= now <= data.get("hasta")

def _validar_items(items: List[Dict[str, object]]) -> List[str]:
    """
    Devuelve lista de errores; vacía si todo OK.
    Reglas: qty >=1, qty <= MAX_QTY_PER_ITEM, y qty <= STOCK[sku] si existe.
    """
    errores: List[str] = []
    if not items:
        return ["El carrito está vacío."]

    for it in items:
        sku = str(it.get("sku", "")).strip()
        try:
            qty = int(it.get("qty") or 0)
        except Exception:
            qty = 0

        if qty < 1:
            errores.append(f"{sku}: cantidad mínima 1.")
        if qty > MAX_QTY_PER_ITEM:
            errores.append(f"{sku}: supera el máximo ({MAX_QTY_PER_ITEM}).")
        if sku in STOCK and qty > STOCK[sku]:
            errores.append(f"{sku}: sin stock suficiente (disp: {STOCK[sku]}).")
    return errores

@require_POST
def api_validar_cupon(request: HttpRequest) -> JsonResponse:
    """
    Entrada: { "codigo": "ECO10", "subtotal": 39990 }
    Salida:  { "ok": true, "percent": 10, "nuevo_total": 35991 }
    Reglas: cupón activo y vigente en ventana temporal.
    """
    body = _json_body(request)
    codigo = (body.get("codigo") or "").strip().upper()
    try:
        subtotal = float(body.get("subtotal") or 0)
    except Exception:
        subtotal = 0.0

    data = CUPONES.get(codigo)
    if not data or not _cupon_vigente(data):
        return JsonResponse({"ok": False, "error": "Cupón inválido o vencido."}, status=400)

    percent = int(data["percent"])
    nuevo_total = round(subtotal * (1 - percent / 100), 2)
    return JsonResponse({"ok": True, "percent": percent, "nuevo_total": nuevo_total})

@require_POST
def api_carrito_validar(request: HttpRequest) -> JsonResponse:
    """
    Entrada: { "items": [ { "sku":"SKU-001", "qty": 3 }, ... ] }
    Salida OK: { "ok": true }
    Salida error: { "ok": false, "errores": ["..."] }
    """
    body = _json_body(request)
    items = body.get("items") or []
    errores = _validar_items(items)
    if errores:
        return JsonResponse({"ok": False, "errores": errores}, status=400)
    return JsonResponse({"ok": True})

@require_POST
def api_checkout_simulado(request: HttpRequest) -> JsonResponse:
    """
    “Confirma” la compra si pasa validaciones.
    Entrada: {
      "email": "persona@mail.com",
      "items": [ { "sku":"SKU-001", "qty": 2, "unit": 19990 }, ... ],
      "cupon": "ECO10" (opcional)
    }
    Reglas: carrito válido, aplica cupón vigente, retorna total_final.
    """
    body = _json_body(request)
    email = (body.get("email") or "").strip()
    items = body.get("items") or []
    cupon = (body.get("cupon") or "").strip().upper() or None

    # 1) validar carrito
    errores = _validar_items(items)
    if errores:
        return JsonResponse({"ok": False, "errores": errores}, status=400)

    # 2) subtotal
    subtotal = 0.0
    for it in items:
        try:
            qty = int(it.get("qty") or 0)
            unit = float(it.get("unit") or 0)
        except Exception:
            qty, unit = 0, 0.0
        subtotal += qty * unit
    subtotal = round(subtotal, 2)

    total = subtotal
    percent = 0

    # 3) cupón (opcional)
    if cupon:
        data = CUPONES.get(cupon)
        if not data or not _cupon_vigente(data):
            return JsonResponse({"ok": False, "error": "Cupón inválido o vencido."}, status=400)
        percent = int(data["percent"])
        total = round(subtotal * (1 - percent / 100), 2)

    # (Si luego persistes pedido en DB, este es el lugar.)
    return JsonResponse({
        "ok": True,
        "email": email,
        "subtotal": subtotal,
        "cupon": cupon,
        "percent": percent,
        "total_final": total
    })