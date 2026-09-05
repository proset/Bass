"""
catalog_builder.py — Mini-catálogo de curvas de adopción (OWID).
Cada país×tecnología = una curva. Salida: data/catalog/curves.json
"""
import pandas as pd
import requests
from io import StringIO
import json
import os

CATALOG_DIR = "data/catalog"

DATASETS = [
    {
        "name": "internet", 
        "categoria": "conectividad",
        "url": "https://ourworldindata.org/grapher/share-of-individuals-using-the-internet.csv?v=1&csvType=full&useColumnShortNames=true",
        "normalization": "percent"
    },
    {
        "name": "electricidad", 
        "categoria": "infraestructura",
        "url": "https://ourworldindata.org/grapher/share-of-the-population-with-access-to-electricity.csv?v=1&csvType=full&useColumnShortNames=true",
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
    # permitir caídas mínimas (<2%) por ruido de medición
    for i in range(1, len(vals)):
        if vals[i] < vals[i-1] * 0.98: return False
    return True

def build_catalog():
    curves = []
    for ds in DATASETS:
        print(f"Descargando {ds['name']}...")
        try:
            r = requests.get(ds["url"], headers=headers)
            r.raise_for_status()
            df = pd.read_csv(StringIO(r.text))
            df.columns = [c.capitalize() for c in df.columns]
        except Exception as e:
            print(f"Error con {ds['name']}: {e}")
            continue

        value_col = [c for c in df.columns if c not in ("Entity", "Code", "Year")][0]
        
        for entity, group in df.groupby("Entity"):
            if entity in AGGREGATES: continue
            
            serie = group.sort_values("Year")
            
            # FILTROS DE CALIDAD (el prior honesto):
            if len(serie) < 15: continue          # madura
            
            vals_raw = serie[value_col].astype(float).values
            scale = 100.0 if ds["normalization"] in ("percent", "per100") else 1.0 
            # Note: The prompt says "Normalización: todo a fracción 0-1 (per-100 -> /100)"
            # Both "percent" and "per100" are just divided by 100.
            vals = vals_raw / scale               # 0-1
            
            if vals[-1] < 0.30: continue          # llegó a adoptar (≥30%)
            if vals[0] > 0.05: continue           # vemos el despegue (<5%)
            if not strictly_monotone(vals): continue  # adopción acumulada limpia
            
            curves.append({
                "id": f"{ds['name']}_{entity}",
                "tecnologia": ds["name"],
                "categoria": ds["categoria"],
                "pais": entity,
                "years": serie["Year"].tolist(),
                "values": [round(float(v), 4) for v in vals],
                "fuente": "OWID",
            })
            
    os.makedirs(CATALOG_DIR, exist_ok=True)
    with open(f"{CATALOG_DIR}/curves.json", "w", encoding="utf-8") as f:
        json.dump(curves, f, indent=1)
        
    # Resumen
    by_cat = {}
    for c in curves:
        by_cat.setdefault(c["categoria"], set()).add(c["id"])
        
    print(f"\nCatálogo: {len(curves)} curvas guardadas en {CATALOG_DIR}/curves.json")
    for cat, ids in by_cat.items():
        print(f"  {cat}: {len(ids)} curvas")

if __name__ == "__main__":
    build_catalog()
