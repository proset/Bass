from __future__ import annotations

import re
import sys
from typing import Dict, List, Optional, Tuple

from report_generator import generate_report
from report_validator import (
    validate_report,
    Finding,
    ValidationResult,
)


# =========================================================================
# Aplicacion automatica de correcciones
# =========================================================================

def _apply_correction(report_md: str, finding: Finding) -> str:
    """
    Aplica una correccion individual al Markdown segun el check_id.
    Devuelve el Markdown modificado.
    """
    cid = finding.check_id

    # --- MATH-10a: R2 equivocado en nota MATH-09 ---
    if cid == "MATH-10" and "R²=" in finding.correction:
        m = re.search(r"Sustituir R[²2]=(\d+\.\d+) por R[²2]=(\d+\.\d+)",
                      finding.correction)
        if m:
            old_r2, new_r2 = m.group(1), m.group(2)
            report_md = report_md.replace(f"R²={old_r2}", f"R²={new_r2}")
            report_md = report_md.replace(f"R2={old_r2}", f"R²={new_r2}")

    # --- MATH-10b: MAPE equivocado en nota MATH-09 ---
    if cid == "MATH-10" and "MAPE=" in finding.correction:
        m = re.search(r"Sustituir MAPE=(\d+\.\d+)% por MAPE=(\d+\.\d+)%",
                      finding.correction)
        if m:
            old_mape, new_mape = m.group(1), m.group(2)
            report_md = report_md.replace(
                f"MAPE={old_mape}%", f"MAPE={new_mape}%"
            )

    # --- MATH-10c: modelo ideal equivocado en nota MATH-09 ---
    if cid == "MATH-10" and "Sustituir '" in finding.correction:
        m = re.search(
            r"Sustituir '(.+?)' por '(.+?)' en la nota MATH-09",
            finding.correction,
        )
        if m:
            old_model, new_model = m.group(1), m.group(2)
            idx = report_md.lower().find("math-09")
            if idx != -1:
                note_end = report_md.find("**", idx + 10)
                if note_end == -1:
                    note_end = len(report_md)
                note_block = report_md[idx:note_end]
                note_block = note_block.replace(old_model, new_model)
                report_md = report_md[:idx] + note_block + report_md[note_end:]

    # --- MATH-11: anadir grupo alias no declarado a la nota MATH-07 ---
    if cid == "MATH-11" and "Añadir a la nota MATH-07:" in finding.correction:
        addition = finding.correction.split("Añadir a la nota MATH-07:")[1].strip()
        idx = report_md.lower().find("math-07")
        if idx != -1:
            note_end = report_md.find("**", idx + 10)
            if note_end == -1:
                note_end = len(report_md)
            report_md = (
                report_md[:note_end - 2]
                + " "
                + addition
                + report_md[note_end - 2:]
            )

    # --- LEX-02: eliminar termino heredado ---
    if cid == "LEX-02" and "Eliminar o sustituir" in finding.correction:
        m = re.search(r"'(.+?)' por término", finding.correction)
        if m:
            bad_term = m.group(1)
            report_md = report_md.replace(
                bad_term,
                finding.message.split("'")[3] if "'" in finding.message
                else "",
            )

    # --- MATH-01: "+0.0%" -> "n/a" cuando real=0 ---
    if cid == "MATH-01":
        for line in report_md.splitlines():
            if "+0.0%" in line and finding.message[:20] in line[:50]:
                report_md = report_md.replace(line, line.replace("+0.0%", "n/a"))

    # --- MATH-08: sustituir cifra narrativa ---
    if cid == "MATH-08" and "Sustituir" in finding.correction:
        m = re.search(
            r"Sustituir '(\d+\.?\d*) millones' por '(\d+\.?\d*) millones'",
            finding.correction,
        )
        if m:
            old_val, new_val = m.group(1), m.group(2)
            report_md = report_md.replace(
                f"{old_val} millones", f"{new_val} millones", 1
            )

    return report_md


def apply_all_corrections(
    report_md: str,
    findings: List[Finding],
) -> str:
    """Aplica todas las correcciones de una lista de findings."""
    # Aplicar correcciones específicas del script
    for f in findings:
        if f.severity == "CRITICAL" and f.correction:
            report_md = _apply_correction(report_md, f)
            
    # Integrar con las correcciones deterministas avanzadas del sistema
    try:
        from apply_deterministic_corrections import apply_deterministic_corrections
        val_res = ValidationResult(findings=findings)
        report_md = apply_deterministic_corrections(report_md, val_res)
    except Exception as e:
        print(f"Nota: No se pudieron aplicar correcciones avanzadas: {e}")
        
    return report_md


# =========================================================================
# Funcion principal del pipeline
# =========================================================================

def generate_and_validate(
    technology: str,
    launch_year: int,
    years: List[int],
    real: List[float],
    context,
    recommended_model: Optional[str] = None,
    issuer: str = "Dirección de Inteligencia de Mercado "
                  "y Planificación Estratégica",
    horizon_years: int = 10,
    max_iterations: int = 3,
    verbose: bool = True,
) -> Tuple[str, ValidationResult]:
    """
    Pipeline end-to-end: genera -> valida -> corrige -> re-valida.

    Parametros:
        technology         : nombre de la tecnologia
        launch_year        : anio t=0
        years, real        : serie historica
        context            : contexto cualitativo (ReportContext/dict/ruta/md)
        recommended_model  : None = inferir automaticamente
        issuer             : firma emisora
        horizon_years      : anios de proyeccion
        max_iterations     : max iteraciones de correccion (default 3)
        verbose            : imprimir progreso

    Retorna:
        (markdown_final, resultado_validacion_final)
        Si no pasa tras max_iterations, devuelve el ultimo Markdown
        con el resultado que tenga (para inspeccion manual).
    """
    # --- Paso 1: Generar ---
    if verbose:
        print(f"[1/4] Generando informe para {technology}...")
    md = generate_report(
        technology=technology,
        launch_year=launch_year,
        years=years,
        real=real,
        context=context,
        recommended_model=recommended_model,
        issuer=issuer,
        horizon_years=horizon_years,
    )

    # Construir parametros para validacion
    real_series = {str(y): v for y, v in zip(years, real)}

    # Extraer proyecciones del Markdown generado para pasarlas al validador
    models_projections = _extract_projections_from_md(md, launch_year, years)

    # Extraer consenso del Markdown
    consensus = _extract_consensus_from_md(md)

    # --- Iteracion: validar -> corregir -> re-validar ---
    result = None
    for iteration in range(1, max_iterations + 1):
        if verbose:
            print(f"[2/4] Validacion iteracion {iteration}/{max_iterations}...")

        result = validate_report(
            report_md=md,
            technology=technology,
            launch_year=launch_year,
            real_series=real_series,
            models_projections=models_projections,
            consensus=consensus,
        )

        if verbose:
            print(f"      {result.summary()}")
            for f in result.findings:
                if f.severity == "CRITICAL":
                    print(f"      [X] {f.check_id}: {f.message[:80]}")

        # Si no hay CRITICAL, estamos listos
        if not result.has_critical:
            if verbose:
                print(f"[4/4] OK - Informe validado ({result.summary()})")
            return md, result

        # --- Paso 3: Aplicar correcciones automaticas ---
        if verbose:
            n_crit = sum(
                1 for f in result.findings if f.severity == "CRITICAL"
            )
            print(f"[3/4] Aplicando {n_crit} correcciones automaticas...")

        md = apply_all_corrections(md, result.findings)

        # Re-extraer proyecciones y consenso por si cambiaron
        models_projections = _extract_projections_from_md(
            md, launch_year, years
        )
        consensus = _extract_consensus_from_md(md)

    # Si llegamos aqui, no convergio
    if verbose:
        print(f"[!] No convergio tras {max_iterations} iteraciones.")
        print(f"    Hallazgos criticos restantes:")
        for f in result.findings:
            if f.severity == "CRITICAL":
                print(f"    - {f.check_id}: {f.message[:100]}")
                if f.correction:
                    print(f"      correccion: {f.correction[:100]}")

    return md, result


# =========================================================================
# Helpers: extraer proyecciones y consenso del Markdown
# =========================================================================

def _extract_projections_from_md(
    md: str,
    launch_year: int,
    years: List[int],
) -> Dict[str, Dict[str, float]]:
    """
    Extrae la tabla de proyecciones del Markdown generado para pasarla
    al validador (necesaria para MATH-04, MATH-06, MATH-11).

    Busca la seccion '## 4. Proyecciones' y parsea la tabla.
    """
    proj_section = re.search(
        r"## .*Proyecciones.*\n(.*?)(?:\n---|\n##|\Z)",
        md, re.DOTALL | re.IGNORECASE,
    )
    if not proj_section:
        return {}

    table_text = proj_section.group(1)

    rows = re.findall(r"^\|\s*(\d{4})\s*\|(.+?)\|$", table_text, re.MULTILINE)
    if not rows:
        return {}

    header_match = re.search(r"^\|\s*Año\s*\|(.+?)\|$", table_text, re.MULTILINE)
    if not header_match:
        return {}

    header_cols = [c.strip() for c in header_match.group(1).split("|")]
    model_names = [re.sub(r"\s*\(M\)\s*$", "", c).strip() for c in header_cols]

    projections: Dict[str, Dict[str, float]] = {}
    for year_str, values_str in rows:
        values = [v.strip() for v in values_str.split("|")]
        for i, val in enumerate(values):
            if i >= len(model_names):
                break
            name = model_names[i]
            try:
                v = float(val)
            except ValueError:
                continue
            projections.setdefault(name, {})[year_str] = v

    return projections


def _extract_consensus_from_md(md: str) -> Dict[str, float]:
    """
    Extrae las cifras de consenso (Hito 2030, Hito 2035) del Markdown.
    Busca patrones como "Hito 2030 ... 134.99 Millones".
    """
    consensus = {}

    patterns = [
        r"Hito\s+(\d{4}).*?(\d+\.\d+)\s*Millones",
        r"Hito\s+(\d{4}).*?(\d+\.\d+)\s*millones",
        r"(\d{4}).*?(\d+\.\d+)\s*Millones.*?Acumulados",
    ]

    for p in patterns:
        for m in re.finditer(p, md, re.IGNORECASE):
            year, val = m.group(1), m.group(2)
            try:
                consensus[year] = float(val)
            except ValueError:
                continue

    return consensus


# =========================================================================
# CLI
# =========================================================================

if __name__ == "__main__":
    import argparse
    import json

    p = argparse.ArgumentParser(
        description="Genera y valida un informe de adopcion en un solo paso."
    )
    p.add_argument("--technology", required=True)
    p.add_argument("--launch-year", type=int, required=True)
    p.add_argument(
        "--series-file", required=True,
        help='Fichero JSON con {"years":[...],"real":[...]}',
    )
    p.add_argument(
        "--context", default=None,
        help="Ruta a fichero contexto.md con marcadores ##",
    )
    p.add_argument(
        "--recommended", default=None,
        help="Modelo recomendado (None = inferir automaticamente)",
    )
    p.add_argument("--output", default=None, help="Ruta de salida .md")
    p.add_argument(
        "--max-iterations", type=int, default=3,
        help="Max iteraciones de correccion (default 3)",
    )
    p.add_argument(
        "--quiet", action="store_true",
        help="No imprimir progreso",
    )
    args = p.parse_args()

    with open(args.series_file, encoding="utf-8") as f:
        series = json.load(f)

    md, result = generate_and_validate(
        technology=args.technology,
        launch_year=args.launch_year,
        years=series["years"],
        real=series["real"],
        context=args.context,
        recommended_model=args.recommended,
        max_iterations=args.max_iterations,
        verbose=not args.quiet,
    )

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"\nInforme guardado: {args.output}")

    print(f"\n{result.summary()}")

    if result.has_critical:
        print("\n[!] HALLAZGOS CRITICOS NO RESUELTOS:")
        for f in result.findings:
            if f.severity == "CRITICAL":
                print(f"  - {f.check_id}: {f.message}")
                if f.correction:
                    print(f"    correccion: {f.correction}")

    sys.exit(0 if not result.has_critical else 1)
