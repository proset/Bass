#!/usr/bin/env python
"""
generate_report.py — One-click pipeline for generating diffusion model reports.

Usage:
  python generate_report.py <tech>

Examples:
  python generate_report.py "meta quest"
  python generate_report.py spotify
  python generate_report.py "vr devices"

Steps:
  1. Check if tech exists in BD
  2. If existing: clean 2026 + old qualitative analysis
     If new: extract via Gemini+Grounding (save BOTH outputs)
  3. Verify BD (monotonic, no 2026, >=5 points)
  4. Fit (persist_fit.py in GLM project)
  5. Compile (compilar_informe_global_con_retry, Groq, auto-retry)
  6. Backends (test_backends.py gemini + claude)
  7. Greps (structural verification)
  8. Report results (no auto-commit)
"""

import sys
import os
import subprocess
import re

BASS_DIR = r"C:\Users\roset\Bass"
GLM_DIR = r"C:\Users\roset\GLM"

sys.path.insert(0, BASS_DIR)

def log(step, msg):
    print(f"[{step}] {msg}")

def call_glm_loaders(tech):
    import json
    import subprocess
    script = f"""
import json
from data.loaders import load_series_for_fit
try:
    s = load_series_for_fit('{tech}')
    # s is a dict with 'years', 'adoptions', 'validation'
    # 'validation' is a ValidationResult object with .ok and .errors
    res = {{
        "ok": True,
        "n": len(s["years"]),
        "years": [int(y) for y in s["years"]],
        "validation_ok": s["validation"].ok,
        "errors": s["validation"].errors
    }}
    print(json.dumps(res))
except Exception as e:
    print(json.dumps({{"ok": False, "error": str(e)}}))
"""
    result = subprocess.run(["python", "-c", script], cwd=GLM_DIR, capture_output=True, text=True)
    try:
        return json.loads(result.stdout.strip())
    except:
        return {"ok": False, "error": result.stderr}

def check_tech_exists(tech):
    """Check if tech has data in BD."""
    res = call_glm_loaders(tech)
    if res.get("ok"):
        return res.get("n", 0) > 0, res
    return False, None

def clean_bd(tech):
    """Delete 2026 rows and old qualitative analysis."""
    from config import get_conn, release_conn
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute(
        "DELETE FROM historical_adoption WHERE tecnologia = %s AND anio = 2026",
        (tech,),
    )
    data_deleted = cur.rowcount
    
    cur.execute(
        "DELETE FROM qualitative_analysis WHERE LOWER(TRIM(tecnologia)) = %s",
        (tech.lower().strip(),),
    )
    qa_deleted = cur.rowcount
    
    conn.commit()
    release_conn(conn)
    log("clean", f"Deleted {data_deleted} data rows (2026) + {qa_deleted} qualitative analysis rows")
    return data_deleted + qa_deleted

def extract_tech(tech):
    """Extract data using Gemini + Google Search Grounding. Save BOTH outputs."""
    from ai.analysis import obtener_datos_y_analisis_ia
    from data.ingestion import insertar_historico_db, guardar_analisis_cualitativo
    
    log("extract", f"Extracting data for '{tech}' via Gemini + Grounding...")
    datos, analisis_text = obtener_datos_y_analisis_ia(tech)
    
    # CRITICAL: save BOTH outputs (lesson from IA certification)
    insertar_historico_db(tech, datos)
    guardar_analisis_cualitativo(tech, analisis_text)
    
    log("extract", f"Extracted {len(datos)} data points + qualitative analysis saved")
    return datos

def verify_bd(tech):
    """Verify the series in BD."""
    res = call_glm_loaders(tech)
    if not res.get("ok"):
        log("verify", f"ERROR loading series: {res.get('error')}")
        return False
        
    n = res.get("n", 0)
    years = res.get("years", [])
    log("verify", f"Points: {n}")
    
    if n > 0:
        log("verify", f"Years: {years[0]} - {years[-1]}")
    log("verify", f"Validation: ok={res.get('validation_ok')}")
    
    if res.get("errors"):
        log("verify", f"ERRORS: {res.get('errors')}")
        return False
        
    if n < 5:
        log("verify", f"ERROR: Only {n} points (minimum 5 required)")
        return False
        
    if n < 10:
        log("verify", f"WARNING: Only {n} points (10+ recommended)")
        
    if 2026 in years:
        log("verify", "WARNING: 2026 in series — cleaning...")
        clean_bd(tech)
        res = call_glm_loaders(tech)
        log("verify", f"After clean: {res.get('n', 0)} points")
        
    return True

def fit_tech(tech):
    """Fit models using persist_fit.py in GLM project."""
    log("fit", f"Fitting models for '{tech}'...")
    result = subprocess.run(
        ["python", "persist_fit.py", tech],
        cwd=GLM_DIR,
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
        
    if result.returncode != 0:
        log("fit", f"ERROR: persist_fit failed (exit {result.returncode})")
        return False
    return True

def compile_report(tech):
    """Compile report with auto-retry (Groq)."""
    import shutil
    for folder in [BASS_DIR, os.path.join(BASS_DIR, "data"), os.path.join(BASS_DIR, "ai")]:
        cache_dir = os.path.join(folder, "__pycache__")
        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)
    log("compile", "Cleared __pycache__ folders")
        
    from data.report_compiler import compilar_informe_global_con_retry
    log("compile", f"Compiling report (Groq, auto-retry)...")
    result = compilar_informe_global_con_retry(tech, force_consenso=True)
    
    if result is True:
        log("compile", "GATE:True")
        return True
    else:
        log("compile", "GATE:False after retries — check output")
        return False

def run_backends(tech):
    """Run backend tests (Gemini + Claude)."""
    log("backends", "Running backends...")
    for backend in ["gemini", "claude"]:
        result = subprocess.run(
            ["python", "test_backends.py", backend, tech],
            cwd=BASS_DIR,
            capture_output=True,
            text=True,
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr)

def run_greps(tech):
    """Run structural greps on the report."""
    report_path = os.path.join(BASS_DIR, f"informe_global_{tech}.md")
    
    if not os.path.exists(report_path):
        log("greps", f"WARNING: Report not found: {report_path}")
        return False
        
    log("greps", f"Grepping {report_path}...")
    with open(report_path, encoding="utf-8") as f:
        content = f.read()
        
    greps = [
        ("Datos oficiales (del motor)", r"Datos oficiales \(del motor\)", ">=2"),
        ("400.00 M (ghost)", r"400\.00 M", "=0"),
        ("Formulations", r"exp\(|dN/dt|Formulación|📐", ">=1"),
        ("1969 (Fix 26)", r"1969", ">=1"),
    ]
    
    for name, pattern, expected in greps:
        matches = re.findall(pattern, content)
        log("greps", f"  {name}: {len(matches)} hits (expected: {expected})")
        
    return True

def main():
    if len(sys.argv) < 2:
        print("Uso: python generate_report.py <tech>")
        print("Ejemplos:")
        print('  python generate_report.py "meta quest"')
        print("  python generate_report.py spotify")
        sys.exit(1)
        
    tech = sys.argv[1]
    
    print(f"\n{'=' * 60}")
    print(f"  GENERATE REPORT: '{tech}'")
    print(f"{'=' * 60}\n")
    
    # Step 1: Check if tech exists
    log("1/7", "Checking if tech exists in BD...")
    exists, _ = check_tech_exists(tech)
    
    if exists:
        log("1/7", "Tech exists — cleaning BD (2026 + old qualitative)...")
        clean_bd(tech)
    else:
        log("1/7", "Tech is NEW — extracting via Gemini+Grounding...")
        extract_tech(tech)
        
    # Step 2: Verify BD
    log("2/7", "Verifying BD...")
    if not verify_bd(tech):
        print("\n*** ABORTED: BD verification failed. ***")
        sys.exit(1)
        
    # Step 3: Fit
    log("3/7", "Fitting models...")
    if not fit_tech(tech):
        print("\n*** ABORTED: Fit failed. ***")
        sys.exit(1)
        
    # Step 4: Compile
    log("4/7", "Compiling report (Groq, auto-retry)...")
    compile_success = compile_report(tech)
    
    # Step 5: Backends
    log("5/7", "Running backends (Gemini + Claude)...")
    run_backends(tech)
    
    # Step 6: Greps
    log("6/7", "Running structural greps...")
    run_greps(tech)
    
    # Step 7: Summary
    log("7/7", "Pipeline complete.")
    
    report_file = f"informe_global_{tech}.md"
    print(f"\n{'=' * 60}")
    print(f"  REPORT: {report_file}")
    print(f"  GATE:   {'True' if compile_success else 'False'}")
    print(f"  Review and commit when satisfied:")
    print(f'    git add "{report_file}"')
    print(f'    git commit -m "Cert {tech}: ..."')
    print(f"{'=' * 60}\n")

if __name__ == "__main__":
    main()
