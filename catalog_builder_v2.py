import pandas as pd
import requests
from io import StringIO
import json
import os
import numpy as np
from config import get_conn, release_conn

CATALOG_DIR = "data/catalog"

# CAPA 1: OWID
DATASETS = [
    {
        "name": "internet", 
        "categoria": "conectividad",
        "url": "https://ourworldindata.org/grapher/share-of-individuals-using-the-internet.csv?v=1&csvType=full&useColumnShortNames=true",
        "normalization": "percent"
    },
    {
        "name": "movil", 
        "categoria": "conectividad",
        "url": "https://ourworldindata.org/grapher/mobile-cellular-subscriptions-per-100-people.csv?v=1&csvType=full&useColumnShortNames=true",
        "normalization": "per100"
    },
    {
        "name": "fija", 
        "categoria": "conectividad",
        "url": "https://ourworldindata.org/grapher/fixed-telephone-subscriptions-per-100-people.csv?v=1&csvType=full&useColumnShortNames=true",
        "normalization": "per100"
    },
    {
        "name": "banda_ancha", 
        "categoria": "conectividad",
        "url": "https://ourworldindata.org/grapher/broadband-penetration-by-country.csv?v=1&csvType=full&useColumnShortNames=true",
        "normalization": "per100"
    },
    {
        "name": "ev_sales_share", 
        "categoria": "ev",
        "url": "https://ourworldindata.org/grapher/electric-car-sales-share.csv?v=1&csvType=full&useColumnShortNames=true",
        "normalization": "percent"
    },
    {
        "name": "vaccine_dtp",
        "categoria": "salud",
        "url": "https://ourworldindata.org/grapher/vaccination-coverage-who-unicef.csv?v=1&csvType=full&useColumnShortNames=true",
        "normalization": "percent"
    }
]

AGGREGATES = {
    "World", "Europe", "Asia", "Africa", "North America", 
    "South America", "Oceania", "European Union",
    "High-income countries", "Low-income countries",
    "Upper-middle-income countries", "Lower-middle-income countries",
    "North America (WB)", "East Asia & Pacific (WB)"
}

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

def strictly_monotone(vals):
    for i in range(1, len(vals)):
        if vals[i] < vals[i-1] * 0.98: return False
    return True

def classify_rhythm(vals):
    # start = first value > 1%
    start_idx = next((i for i, v in enumerate(vals) if v > 0.01), -1)
    if start_idx == -1 or start_idx + 4 >= len(vals):
        return "Desconocido" # Cannot determine year 5
    v2 = vals[start_idx + 1] # Year 2 (index start+1)
    v5 = vals[start_idx + 4] # Year 5 (index start+4)
    if v2 == 0:
        return "Explosiva"
    ratio = v5 / v2
    
    # Thresholds ajustados a >5x tras revisión con FB/TikTok
    if ratio > 5.0:
        return "Explosiva"
    elif ratio >= 2.0:
        return "Media"
    else:
        return "Gradual"

def get_db_series(tech_name):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT anio, adopcion_acumulada FROM historical_adoption WHERE tecnologia = %s ORDER BY anio", (tech_name,))
    data = cur.fetchall()
    release_conn(conn)
    if not data:
        return [], []
    years = [int(r[0]) for r in data]
    vals = [float(r[1]) for r in data]
    return years, vals

# MAU series in Millions (approximate historical data)
facebook_y = list(range(2004, 2024))
facebook_v = [1, 5, 12, 58, 145, 360, 608, 845, 1056, 1230, 1390, 1590, 1860, 2130, 2320, 2500, 2800, 2910, 2960, 3050]
whatsapp_y = list(range(2009, 2024))
whatsapp_v = [1, 10, 50, 100, 400, 600, 900, 1000, 1300, 1500, 1600, 2000, 2000, 2000, 2780]
youtube_y = list(range(2005, 2024))
youtube_v = [2, 20, 50, 100, 200, 400, 800, 1000, 1000, 1100, 1300, 1500, 1500, 1800, 2000, 2290, 2560, 2560, 2700]
twitter_y = list(range(2006, 2024))
twitter_v = [0.1, 0.5, 3, 18, 54, 117, 185, 241, 288, 305, 318, 330, 321, 330, 353, 396, 368, 368]
snapchat_y = list(range(2011, 2024))
snapchat_v = [1, 10, 30, 60, 107, 158, 178, 186, 218, 265, 319, 375, 414]

SOCIAL_MEDIA = {
    "Facebook": (facebook_y, facebook_v, 3050.0),
    "WhatsApp": (whatsapp_y, whatsapp_v, 2780.0),
    "YouTube": (youtube_y, youtube_v, 2700.0),
    "Twitter": (twitter_y, twitter_v, 400.0),
    "Snapchat": (snapchat_y, snapchat_v, 500.0)
}

# Consumer tech series (approximate % household penetration US)
CONSUMER_TECH = {
    "Color_TV": (list(range(1964, 1979)), [3, 5, 8, 15, 24, 33, 43, 53, 62, 70, 74, 77, 80, 82, 85], 100.0),
    "VCR": (list(range(1980, 1995)), [1, 2, 4, 9, 17, 28, 40, 50, 60, 68, 72, 75, 77, 79, 81], 100.0),
    "DVD": (list(range(1999, 2011)), [5, 12, 23, 36, 50, 63, 75, 80, 83, 85, 87, 89], 100.0),
    "Smartphones_US": (list(range(2007, 2020)), [5, 10, 17, 27, 42, 53, 65, 72, 77, 81, 83, 85, 86], 100.0),
    "Tablets_US": (list(range(2010, 2020)), [3, 11, 23, 35, 45, 51, 54, 56, 58, 60], 100.0),
}

def print_debug_classification(name, vals, ceil):
    v_norm = np.array(vals) / ceil
    start_idx = next((i for i, v in enumerate(v_norm) if v > 0.01), -1)
    if start_idx == -1 or start_idx + 4 >= len(v_norm):
        print(f"DEBUG {name:15s}: Desconocido (Start={start_idx})")
        return
    v2 = v_norm[start_idx + 1]
    v5 = v_norm[start_idx + 4]
    ratio = v5 / v2 if v2 > 0 else float('inf')
    cls = "Explosiva" if ratio > 5.0 else ("Media" if ratio >= 2.0 else "Gradual")
    print(f"DEBUG {name:15s}: Año 1 (v={v_norm[start_idx]:.3f}) | Año 2 (v={v2:.3f}) | Año 5 (v={v5:.3f}) => Ratio: {ratio:5.1f}x -> {cls}")

def build_catalog():
    curves = []
    
    # Debug de las redes
    print("\n--- DEBUG REDES SOCIALES ---")
    for net, (_, v, ceil) in SOCIAL_MEDIA.items():
        print_debug_classification(net, v, ceil)
    for tech in ["instagram", "tiktok"]:
        _, v = get_db_series(tech)
        if v:
            print_debug_classification(tech, v, max(v)*1.1)
    print("----------------------------\n")

    # 1. OWID
    for ds in DATASETS:
        print(f"Descargando {ds['name']}...")
        try:
            r = requests.get(ds["url"], headers=headers)
            if r.status_code != 200:
                continue
            df = pd.read_csv(StringIO(r.text))
            df.columns = [c.capitalize() for c in df.columns]
        except Exception as e:
            continue

        valid_cols = [c for c in df.columns if c not in ("Entity", "Code", "Year")]
        if not valid_cols:
            continue
        value_col = valid_cols[0]
        
        for entity, group in df.groupby("Entity"):
            if entity in AGGREGATES: continue
            serie = group.sort_values("Year")
            if len(serie) < 15: continue
            
            vals_raw = serie[value_col].astype(float).values
            scale = 100.0 if ds["normalization"] in ("percent", "per100") else 1.0 
            vals = vals_raw / scale
            
            if vals[-1] < 0.30: continue
            if vals[0] > 0.05: continue
            if not strictly_monotone(vals): continue
            
            ritmo = classify_rhythm(vals)
            
            curves.append({
                "id": f"{ds['name']}_{entity}",
                "tecnologia": ds["name"],
                "categoria": ds["categoria"],
                "pais": entity,
                "years": serie["Year"].tolist(),
                "values": [round(float(v), 4) for v in vals],
                "fuente": "OWID",
                "ritmo": ritmo
            })

    # 2. SOCIAL MEDIA CAPA 2
    for net_name, (y, v, ceil) in SOCIAL_MEDIA.items():
        vals = np.array(v) / ceil
        ritmo = classify_rhythm(vals)
        curves.append({
            "id": f"sm_{net_name}",
            "tecnologia": net_name,
            "categoria": "redes-sociales",
            "pais": "Global",
            "years": y,
            "values": [round(float(val), 4) for val in vals],
            "fuente": "Public MAU",
            "ritmo": ritmo,
            "values_abs": v
        })

    # Add DB Social Media
    for tech in ["instagram", "tiktok"]:
        y, v = get_db_series(tech)
        if y:
            ceil = max(v) * 1.1
            vals = np.array(v) / ceil
            ritmo = classify_rhythm(vals)
            curves.append({
                "id": f"sm_{tech}",
                "tecnologia": tech,
                "categoria": "redes-sociales",
                "pais": "Global",
                "years": y,
                "values": [round(float(val), 4) for val in vals],
                "fuente": "DB historical",
                "ritmo": ritmo,
                "values_abs": v
            })

    # 3. CONSUMER TECH CAPA 3
    for tech, (y, v, ceil) in CONSUMER_TECH.items():
        vals = np.array(v) / ceil
        ritmo = classify_rhythm(vals)
        curves.append({
            "id": f"hw_{tech}",
            "tecnologia": tech,
            "categoria": "consumo",
            "pais": "US",
            "years": y,
            "values": [round(float(val), 4) for val in vals],
            "fuente": "Public Estimates",
            "ritmo": ritmo
        })

    os.makedirs(CATALOG_DIR, exist_ok=True)
    with open(f"{CATALOG_DIR}/curves.json", "w", encoding="utf-8") as f:
        json.dump(curves, f, indent=1)
        
    by_cat = {}
    by_ritmo = {}
    for c in curves:
        by_cat.setdefault(c["categoria"], set()).add(c["id"])
        by_ritmo.setdefault(c["ritmo"], set()).add(c["id"])
        
    print(f"\nCatálogo: {len(curves)} curvas guardadas en {CATALOG_DIR}/curves.json")
    print("\nPor Categoría:")
    for cat, ids in by_cat.items():
        print(f"  {cat}: {len(ids)} curvas")
    print("\nPor Ritmo:")
    for rit, ids in by_ritmo.items():
        print(f"  {rit}: {len(ids)} curvas")

if __name__ == "__main__":
    build_catalog()
