"""
models/analogical_forecast.py — Fix 45: proyección por analogía para young-techs.
Método C del backtest: match por forma (3 primeros años normalizados) + ritmo,
dentro del pool del catálogo. Prior de techo = percentiles de los top-K análogos.
"""
import json
import numpy as np
from scipy.optimize import curve_fit

CATALOG_PATH = "data/catalog/curves.json"
K_ANALOGOS = 20

def load_catalog():
    with open(CATALOG_PATH, encoding="utf-8") as f:
        return json.load(f)

def classify_rhythm(young_series):
    """
    Ritmo de la young tech: ratio año5/año2 desde despegue.
    young_series: valores acumulados (años de vida 0..n).
    Explosiva >5x, Media 2-5x, Gradual <2x.
    """
    vals = np.array(young_series, dtype=float)
    # Despegue: primer valor >1% del último
    if vals[-1] <= 0: return "desconocido"
    threshold = vals[-1] * 0.01
    start = int(np.argmax(vals > threshold))
    if vals[start] <= threshold: return "desconocido"
    if start + 2 >= len(vals):
        return "desconocido"
    y2 = vals[start + 2]
    y5 = vals[start + 5] if start + 5 < len(vals) else vals[-1]
    if y2 <= 0: return "desconocido"
    ratio = y5 / y2
    if ratio > 5: return "explosiva"
    if ratio >= 2: return "media"
    return "gradual"

def find_analogues(young_series, pool_rhythm=None, k=K_ANALOGOS):
    """
    Match por forma: los K análogos del catálogo cuyos primeros 
    len(young) puntos (normalizados por su techo) más se parecen.
    Filtra por clase de ritmo si se especifica.
    Retorna: lista de dicts {id, techo, tecnologia, categoria, distancia}
    """
    catalog = load_catalog()
    yv = np.array(young_series, dtype=float)
    if yv[-1] <= 0: return []
    y_norm = yv / yv[-1]  # normalizada por su último valor
    
    candidates = []
    for c in catalog:
        # Match ignorando mayúsculas y permitiendo compatibilidad con el formato guardado en json ("Explosiva", "Media", "Gradual")
        if pool_rhythm and c.get("ritmo", "").lower() != pool_rhythm.lower():
            continue
        vals = np.array(c["values"])
        techo = vals[-1]
        if techo <= 0: continue
        # Despegue del análogo: primer >1% de su techo
        start = int(np.argmax(vals > techo * 0.01))
        if vals[start] <= techo * 0.01: continue
        if start + len(yv) > len(vals):
            continue  # el análogo no tiene suficientes años post-despegue
        a_norm = vals[start:start + len(yv)] / techo
        d = float(np.linalg.norm(a_norm - y_norm))
        candidates.append({
            "id": c["id"], "techo": float(techo),
            "tecnologia": c["tecnologia"], "categoria": c.get("categoria", "?"),
            "distancia": d,
            "ritmo_catalogo": c.get("ritmo", "Desconocido")
        })
    candidates.sort(key=lambda x: x["distancia"])
    return candidates[:k]

def prior_ceiling(analogues):
    """Percentiles p25/p50/p75 del techo de los análogos."""
    if not analogues: return None
    techos = [a["techo"] for a in analogues]
    p25, p50, p75 = np.percentile(techos, [25, 50, 75])
    return {"conservador": float(p25), "base": float(p50), "optimista": float(p75)}

def fit_with_fixed_ceiling(young_series, ceiling):
    """
    Fit logístico con m FIJADO (2 params: k, t0) sobre la young tech.
    young_series en unidades ABSOLUTAS (M) — el techo viene en unidades
    del catálogo (penetración 0-1 o M absolutos para redes) → 
    ESCALAR el prior al dominio de la young tech ANTES de este fit.
    Retorna (k, t0) o None si no converge.
    """
    t = np.arange(len(young_series), dtype=float)
    yv = np.array(young_series, dtype=float)
    if ceiling <= yv[-1]:
        ceiling = yv[-1] * 1.05 # ensure ceiling is at least current max
    try:
        popt, _ = curve_fit(
            lambda t, k, t0: ceiling / (1 + np.exp(-k * (t - t0))),
            t, yv, p0=[0.5, 1.0], maxfev=5000)
        return tuple(float(v) for v in popt)
    except Exception:
        return None

def project(young_series, params, ceiling, years_ahead=10):
    """Proyección con el fit y el techo fijado."""
    if params is None: return None
    k, t0 = params
    t = np.arange(len(young_series) + years_ahead, dtype=float)
    return ceiling / (1 + np.exp(-k * (t - t0)))
