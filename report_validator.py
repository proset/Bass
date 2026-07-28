"""
report_validator.py
====================
Validador determinístico para informes de adopción tecnológica.

Ejecuta 15 checks léxicos y matemáticos ANTES de invocar al LLM auditor,
para ahorrar tokens y eliminar fallos triviales de forma fiable.

Checks:
  Léxicos:          LEX-01, LEX-02, LEX-03, LEX-04
  Matemáticos:       MATH-01, MATH-02, MATH-03, MATH-04, MATH-05, MATH-06
  Correctivos:       MATH-07 (consolidación de redundancia numérica),
                    MATH-08 (reconciliación narrativa vs tabla),
                    MATH-09 (cláusula estándar por elección teórica R&K)
  Consistencia notas: MATH-10 (nota MATH-09 con modelo/cifras correctos),
                    MATH-11 (nota MATH-07 declara todos los grupos alias)

Uso:
    from report_validator import validate_report
    findings = validate_report(
        report_md=texto_del_informe,
        technology="Grifols",          # nombre de la tecnología analizada
        launch_year=2015,              # año de lanzamiento comercial
        real_series={"2015": 1.0, "2016": 3.0, ...},   # serie histórica real
        models_projections={          # proyecciones por modelo (opcional)
            "Bass Clásico": {"2030": 34.71, "2035": 49.93},
            ...
        },
        consensus={"2030": 36.5, "2035": 51.2},   # pronóstico de consenso
    )
    # findings: lista de Finding(severity, check_id, message, location)

Salida:
    - Lista de Finding objects.
    - Si la lista es vacía → el informe pasa el validador determinístico.
    - Si hay cualquier Finding con severity="CRITICAL" → bloquear publicación.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


# =========================================================================
# Estructura de datos
# =========================================================================

@dataclass
class Finding:
    severity: str           # "CRITICAL" | "WARNING" | "INFO"
    check_id: str           # "LEX-01" | "MATH-05" etc.
    message: str            # descripción del hallazgo
    location: str = ""      # sección / línea / contexto
    correction: str = ""    # corrección propuesta


@dataclass
class ValidationResult:
    findings: List[Finding] = field(default_factory=list)
    passed: bool = True

    @property
    def has_critical(self) -> bool:
        return any(f.severity == "CRITICAL" for f in self.findings)

    @property
    def has_warnings(self) -> bool:
        return any(f.severity == "WARNING" for f in self.findings)

    def summary(self) -> str:
        n_crit = sum(1 for f in self.findings if f.severity == "CRITICAL")
        n_warn = sum(1 for f in self.findings if f.severity == "WARNING")
        n_info = sum(1 for f in self.findings if f.severity == "INFO")
        status = "NO PUBLICABLE" if self.has_critical else (
            "PUBLICABLE TRAS CORRECCIONES MENORES" if self.has_warnings
            else "PUBLICABLE SIN CAMBIOS"
        )
        return (
            f"Veredicto determinístico: {status}\n"
            f"  CRITICAL: {n_crit}\n"
            f"  WARNING:  {n_warn}\n"
            f"  INFO:     {n_info}"
        )


# =========================================================================
# Listas negras configurables
# =========================================================================

# Tecnología equivocada en encabezados / texto (fuga de copy-paste)
_INHERITED_TECH_MARKERS: Dict[str, List[str]] = {
    # technology_name -> términos que NO deberían aparecer si el informe
    # NO es de esa tecnología
    "Gemini": [
        "pgvector & Gemini",
        "Project Astra",
        "Gemini Nano",
        "Gemini Advanced",
        "gemini.google.com",
        "Google One AI Premium",
    ],
    "Grifols": [
        "Grifols",
        "Alphanate",
        "Gamunex",
        "hemoderivados",
    ],
}

# Abreviaturas en inglés que tienen equivalente en español
_ANGlicism_MAP: Dict[str, str] = {
    r"\bGDP\b": "PIB",
    # r"\bASP\b": "ASP",  # en informes farmacéuticos ASP es jerga estándar, permitir
}

# Términos que deben definirse al citarse por primera vez
_UNDEFINED_TERMS_WATCH: List[str] = [
    "parámetros de Hofstede",
    "Hofstede",
    # Añadir otros que aparezcan sin contexto en futuros informes
]


# =========================================================================
# Función principal
# =========================================================================

def validate_report(
    report_md: str,
    technology: str,
    launch_year: int,
    real_series: Optional[Dict[str, float]] = None,
    models_projections: Optional[Dict[str, Dict[str, float]]] = None,
    consensus: Optional[Dict[str, float]] = None,
    inherited_markers: Optional[Dict[str, List[str]]] = None,
) -> ValidationResult:

    result = ValidationResult()
    lines = report_md.splitlines()

    # -----------------------------------------------------------
    # CHECKS LÉXICOS / ESTRUCTURALES
    # -----------------------------------------------------------

    # LEX-01: palabra "billón" / "billones" en sentido inglés
    _check_lex_01_billon(report_md, result)

    # LEX-02: encabezados heredados de otra tecnología
    _check_lex_02_inherited_tech(
        report_md, technology, result, inherited_markers
    )

    # LEX-03: anglicismos evitables (GDP -> PIB)
    _check_lex_03_anglicisms(report_md, result)

    # LEX-04: términos citados sin definir
    _check_lex_04_undefined_terms(report_md, result)

    # -----------------------------------------------------------
    # CHECKS MATEMÁTICOS DETERMINISTAS
    # -----------------------------------------------------------

    # MATH-01: desviación % mostrada como "+0.0%" cuando el real es 0
    _check_math_01_deviation_zero(report_md, real_series, result)

    # MATH-02: MAPE declarado como calculado solo sobre real > 0
    _check_math_02_mape_declaration(report_md, result)

    # MATH-03: modelos con R² idénticos a 4 decimales (aliasing)
    _check_math_03_identical_r2(report_md, result)

    # MATH-04: modelos con predicciones idénticas a 2 decimales
    _check_math_04_identical_predictions(models_projections, result)

    # MATH-05: predicciones no nulas anteriores al lanzamiento
    _check_math_05_prelaunch_artifacts(
        models_projections, launch_year, result
    )

    # MATH-06: consenso no respaldado por ningún modelo
    _check_math_06_consensus_unsupported(
        models_projections, consensus, result
    )

    # -----------------------------------------------------------
    # CHECKS CORRECTIVOS DETERMINISTAS (nuevos)
    # -----------------------------------------------------------

    # MATH-07: consolidación de redundancia numérica (MATH-03/04 → fix)
    _check_math_07_consolidate_redundancy(
        report_md, models_projections, result
    )

    # MATH-08: reconciliación narrativa vs tabla (SEM-01 → fix determinista)
    _check_math_08_narrative_vs_table(report_md, real_series, result)

    # MATH-09: cláusula estándar por elección teórica de R&K (SEM-02 → fix)
    _check_math_09_rk_theoretical_clause(
        report_md, models_projections, result
    )

    # MATH-10: consistencia de la nota MATH-09 (modelo y cifras correctos)
    _check_math_10_math09_consistency(report_md, result)

    # MATH-11: completitud de la nota MATH-07 (todos los grupos alias declarados)
    _check_math_11_math07_completeness(
        report_md, models_projections, result
    )

    # MATH-12: validación de monotonía de la curva de consenso extraída de la narrativa
    _check_math_12_consensus_monotonicity(report_md, result)

    # MATH-13: validación de tech naciente / techo de crecimiento razonable
    _check_math_13_infancy_growth_ceiling(report_md, real_series, result)

    # MATH-14: sanity check geodemográfico
    _check_math_14_geopopulation_sanity_check(report_md, technology, real_series, result)

    # Veredicto final
    result.passed = not result.has_critical
    return result


# =========================================================================
# Implementación de checks léxicos
# =========================================================================

def _check_lex_01_billon(report_md: str, result: ValidationResult) -> None:
    """
    Detecta 'billón' / 'billones' usado en sentido inglés (10^9).
    En español peninsular 'billón' = 10^12.
    """
    pattern = re.compile(r"\bbill[oó]n(?:es)?\b", re.IGNORECASE)
    for i, line in enumerate(report_md.splitlines(), start=1):
        if pattern.search(line):
            result.findings.append(Finding(
                severity="WARNING",
                check_id="LEX-01",
                message=(
                    "Uso de 'billón' en sentido probable inglés (10^9). "
                    "En español 'billón' = 10^12. "
                    "Sustituir por 'mil millones' si la cifra es 10^9."
                ),
                location=f"línea {i}: {line.strip()[:120]}",
                correction="'billón' → 'mil millones'",
            ))


def _check_lex_02_inherited_tech(
    report_md: str,
    technology: str,
    result: ValidationResult,
    inherited_markers: Optional[Dict[str, List[str]]] = None,
) -> None:
    """
    Detecta encabezados / términos heredados de otra tecnología
    (fuga de copy-paste entre informes).
    Ejemplo clásico: 'pgvector & Gemini' en un informe de Grifols.
    """
    markers = inherited_markers or _INHERITED_TECH_MARKERS
    for other_tech, terms in markers.items():
        if other_tech.lower() == technology.lower():
            continue
        for term in terms:
            if term.lower() in report_md.lower():
                # localizar primera ocurrencia
                idx = report_md.lower().find(term.lower())
                line_no = report_md[:idx].count("\n") + 1
                result.findings.append(Finding(
                    severity="CRITICAL",
                    check_id="LEX-02",
                    message=(
                        f"Término heredado de informe de '{other_tech}' "
                        f"detectado en un informe de '{technology}': "
                        f"'{term}'. Probable copy-paste residual."
                    ),
                    location=f"línea {line_no}",
                    correction=f"Eliminar o sustituir '{term}' por término "
                               f"propio de {technology}.",
                ))


def _check_lex_03_anglicisms(
    report_md: str, result: ValidationResult
) -> None:
    """
    Detecta anglicismos evitables que tienen equivalente español.
    """
    for pattern_str, replacement in _ANGlicism_MAP.items():
        for m in re.finditer(pattern_str, report_md):
            line_no = report_md[:m.start()].count("\n") + 1
            result.findings.append(Finding(
                severity="WARNING",
                check_id="LEX-03",
                message=(
                    f"Anglicismo evitable: '{m.group(0)}'. "
                    f"Equivalente español: '{replacement}'."
                ),
                location=f"línea {line_no}",
                correction=f"'{m.group(0)}' → '{replacement}'",
            ))


def _check_lex_04_undefined_terms(
    report_md: str, result: ValidationResult
) -> None:
    """
    Detecta términos técnicos citados de la nada sin definición previa.
    """
    low = report_md.lower()
    for term in _UNDEFINED_TERMS_WATCH:
        if term.lower() in low:
            # verificar si el término está definido/explicado en el cuerpo
            # (heurística simple: buscar appearances múltiples o contexto)
            if low.count(term.lower()) == 1:
                idx = low.find(term.lower())
                line_no = report_md[:idx].count("\n") + 1
                result.findings.append(Finding(
                    severity="WARNING",
                    check_id="LEX-04",
                    message=(
                        f"Término '{term}' citado una sola vez, sin "
                        f"definición previa ni referencia bibliográfica."
                    ),
                    location=f"línea {line_no}",
                    correction=(
                        f"Añadir definición de '{term}' o citar referencia "
                        f"bibliográfica."
                    ),
                ))


# =========================================================================
# Implementación de checks matemáticos
# =========================================================================

def _check_math_01_deviation_zero(
    report_md: str,
    real_series: Optional[Dict[str, float]],
    result: ValidationResult,
) -> None:
    """
    Detecta desviaciones porcentuales reportadas como '+0.0%' en años
    donde el valor real es 0 (la desviación es indefinida por división
    entre cero).
    """
    if not real_series:
        return
    zero_years = {y for y, v in real_series.items() if v == 0.0}
    if not zero_years:
        return

    # buscar filas de tabla que empiecen con un año de real=0
    # y contengan "+0.0%" como desviación
    pattern = re.compile(r"^\|?\s*(\d{4})")
    for i, line in enumerate(report_md.splitlines(), start=1):
        m = pattern.match(line.strip())
        if not m:
            continue
        year = m.group(1)
        if year in zero_years and "+0.0%" in line:
            result.findings.append(Finding(
                severity="CRITICAL",
                check_id="MATH-01",
                message=(
                    f"Desviación reportada como '+0.0%' en año {year} "
                    f"con valor real = 0. La desviación relativa es "
                    f"indefinida (división entre cero)."
                ),
                location=f"línea {i}: {line.strip()[:120]}",
                correction="Marcar como 'n/a' o 'N/D', no '+0.0%'.",
            ))


def _check_math_02_mape_declaration(
    report_md: str, result: ValidationResult
) -> None:
    """
    Verifica que el MAPE se declare como calculado exclusivamente sobre
    años con adopción real > 0.
    """
    low = report_md.lower()
    has_mape = "mape" in low
    if not has_mape:
        return

    # heurística: buscar cláusula declarativa cerca de la palabra MAPE
    declaration_patterns = [
        r"mape[^\n]{0,200}(?:solo|exclusivamente|únicamente)[^\n]{0,100}"
        r"(?:real\s*>\s*0|no nul|non.?null|non.?zero)",
        r"(?:real\s*>\s*0|no nul|non.?null|non.?zero)[^\n]{0,200}"
        r"mape",
    ]
    declared = any(
        re.search(p, low, re.IGNORECASE) for p in declaration_patterns
    )
    if not declared:
        result.findings.append(Finding(
            severity="WARNING",
            check_id="MATH-02",
            message=(
                "Se reporta MAPE pero no se declara explicitamente que "
                "se calcula solo sobre años con adopción real > 0. "
                "Si hay años con real = 0, la MAPE no es calculable."
            ),
            location="sección 'Resumen del Error de Ajuste'",
            correction=(
                "Añadir nota: 'MAPE calculado exclusivamente sobre años "
                "con adopción real > 0.'"
            ),
        ))


def _check_math_03_identical_r2(
    report_md: str, result: ValidationResult
) -> None:
    """
    Detecta modelos con R² idénticos a 4 decimales (sospecha de aliasing
    numérico / colapso de parámetros).
    """
    # buscar tabla de ajuste: Modelo | R² | MAPE
    # heurística: líneas con patrón  NombreModelo  0.xxx  X%
    pattern = re.compile(
        r"^\|?\s*([A-Za-zÉáíóú&\-\.\s]+?)\s*\|\s*"
        r"(-?\d+\.\d{3,4})\s*\|\s*(\d+\.\d{1,2}%?)\s*\|?$"
    )
    r2_map: Dict[str, float] = {}
    for i, line in enumerate(report_md.splitlines(), start=1):
        m = pattern.match(line.strip())
        if not m:
            continue
        model = m.group(1).strip()
        try:
            r2 = float(m.group(2))
        except ValueError:
            continue
        r2_map[model] = r2

    # agrupar modelos por R² idéntico
    by_r2: Dict[float, List[str]] = {}
    for model, r2 in r2_map.items():
        by_r2.setdefault(round(r2, 4), []).append(model)

    for r2, models in by_r2.items():
        if len(models) > 1:
            result.findings.append(Finding(
                severity="WARNING",
                check_id="MATH-03",
                message=(
                    f"Modelos con R² idéntico a 4 decimales ({r2:.4f}): "
                    f"{', '.join(models)}. Posible aliasing numérico o "
                    f"colapso de parámetros. Considerar consolidar."
                ),
                location="tabla 'Resumen del Error de Ajuste'",
                correction=(
                    "Declarar explicitamente cuáles modelos son "
                    "numéricamente indistinguibles y consolidar en uno solo."
                ),
            ))


def _check_math_04_identical_predictions(
    models_projections: Optional[Dict[str, Dict[str, float]]],
    result: ValidationResult,
) -> None:
    """
    Detecta modelos con predicciones idénticas a 2 decimales en toda la
    tabla de proyecciones futuras (sospecha de redundancia numérica).
    """
    if not models_projections or len(models_projections) < 2:
        return

    # normalizar: modelo -> tuple ordenado de (year, round(value,2))
    def signature(proj: Dict[str, float]) -> tuple:
        return tuple(
            round(v, 2) for _, v in sorted(proj.items())
        )

    sig_map: Dict[tuple, List[str]] = {}
    for model, proj in models_projections.items():
        sig = signature(proj)
        sig_map.setdefault(sig, []).append(model)

    for sig, models in sig_map.items():
        if len(models) > 1:
            result.findings.append(Finding(
                severity="WARNING",
                check_id="MATH-04",
                message=(
                    f"Modelos con predicciones idénticas a 2 decimales en "
                    f"toda la tabla de proyecciones: {', '.join(models)}. "
                    f"Son numéricamente indistinguibles; mantener solo uno."
                ),
                location="tabla 'Proyecciones Futuras de Adopción'",
                correction=(
                    f"Consolidar en un único modelo; {', '.join(models[1:])}"
                    f" pueden omitirse del informe principal."
                ),
            ))


def _check_math_05_prelaunch_artifacts(
    models_projections: Optional[Dict[str, Dict[str, float]]],
    launch_year: int,
    result: ValidationResult,
) -> None:
    """
    Detecta predicciones no nulas en años anteriores al lanzamiento
    (artefactos del ajuste sigmoide, no previsiones reales).
    """
    if not models_projections:
        return

    for model, proj in models_projections.items():
        for year_str, value in proj.items():
            try:
                year = int(float(year_str))
            except (ValueError, TypeError):
                continue
            if year < launch_year and abs(value) > 0.01:
                result.findings.append(Finding(
                    severity="INFO",
                    check_id="MATH-05",
                    message=(
                        f"Predicción no nula ({value}) del modelo "
                        f"'{model}' en {year}, anterior al lanzamiento "
                        f"({launch_year}). Es un artefacto del ajuste "
                        f"sigmoide, no una previsión real."
                    ),
                    location=f"tabla proyecciones, año {year}",
                    correction=(
                        "Declarar explicitamente que las predicciones "
                        "pre-launch son artefactos del ajuste."
                    ),
                ))
                break  # un hallazgo por modelo es suficiente


def _check_math_06_consensus_unsupported(
    models_projections: Optional[Dict[str, Dict[str, float]]],
    consensus: Optional[Dict[str, float]],
    result: ValidationResult,
) -> None:
    """
    Detecta cifras del pronóstico de consenso que no coinciden con
    ningún modelo (estimación cualitativa disfrazada de consenso).
    """
    if not consensus or not models_projections:
        return

    tol = 0.5  # tolerancia en millones para considerar 'respaldado'

    for year_str, consensus_val in consensus.items():
        try:
            consensus_v = float(consensus_val)
        except (ValueError, TypeError):
            continue

        supported = False
        supporting_models: List[str] = []
        for model, proj in models_projections.items():
            if year_str in proj:
                try:
                    pv = float(proj[year_str])
                except (ValueError, TypeError):
                    continue
                if abs(pv - consensus_v) <= tol:
                    supported = True
                    supporting_models.append(model)

        if not supported:
            result.findings.append(Finding(
                severity="WARNING",
                check_id="MATH-06",
                message=(
                    f"El pronóstico de consenso para {year_str} "
                    f"({consensus_v}) no coincide (tol ±{tol}M) con "
                    f"ningún modelo. Debe etiquetarse como 'estimación "
                    f"cualitativa del analista', no como 'consenso'."
                ),
                location=f"Pronóstico de Consenso, año {year_str}",
                correction=(
                    "Renombrar la cifra como 'estimación cualitativa' "
                    "o ajustar el consenso al rango de los modelos."
                ),
            ))


# =========================================================================
# Checks correctivos deterministas (nuevos)
# =========================================================================

# Mapeo de modelos a su familia de difusión teórica (para MATH-07).
# Usado al generar la cláusula de consolidación: de cada familia
# numérica idéntica, recomendamos conservar el más representativo.
_MODEL_FAMILY_PREFERENCE = [
    # (familia, modelo preferido para conservar, razón teórica)
    ("Roset & Canals", "Roset & Canals", "lectura del abismo de Moore"),
    ("Van den Bulte & Joshi", "Roset & Canals", "redundante con Roset & Canals"),
    ("Muller & Yogev", "Roset & Canals", "redundante con Roset & Canals"),
    ("Ladrón-de-Guevara & Putsis", "Bass Clásico",
     "R²/MAPE idénticos a Bass en este ajuste"),
]


def _check_math_07_consolidate_redundancy(
    report_md: str,
    models_projections: Optional[Dict[str, Dict[str, float]]],
    result: ValidationResult,
) -> None:
    """
    MATH-07 — Corrección automática de la redundancia numérica
    detectada por MATH-03/MATH-04.

    Si se identifican modelos alias (R² idénticos o predicciones idénticas),
    genera una CORRECCIÓN estándar lista para insertar en el informe,
    declarando:
      - cuáles modelos son numéricamente indistinguibles,
      - cuál conservar,
      - que el ajuste empírico no distingue entre ellos y la elección
        se hace por coherencia teórica.

    No actúa si no hay redundancia (en cuyo caso MATH-03/MATH-04 no lanzan
    warnings y aquí no se hace nada).
    """
    if not models_projections or len(models_projections) < 2:
        return

    # 1. Recalcular familias numéricas por predicciones idénticas
    def signature(proj):
        return tuple(round(v, 2) for _, v in sorted(proj.items()))

    sig_groups: Dict[tuple, List[str]] = {}
    for model, proj in models_projections.items():
        sig = signature(proj)
        sig_groups.setdefault(sig, []).append(model)

    redundant_groups = [g for g in sig_groups.values() if len(g) > 1]
    if not redundant_groups:
        return

    # 2. Generar cláusula de consolidación unificada para todos los grupos redundantes
    clauses = []
    for group in redundant_groups:
        # elegir cuál conservar de acuerdo a _MODEL_FAMILY_PREFERENCE
        keep = group[0]
        for fam, preferred, _reason in _MODEL_FAMILY_PREFERENCE:
            if preferred in group:
                keep = preferred
                break

        aliases = [m for m in group if m != keep]
        aliases_str = ", ".join(aliases)
        clauses.append(
            f"los modelos {', '.join(group)} presentan predicciones numéricamente "
            f"indistinguibles a 2 decimales en toda la tabla de proyecciones "
            f"(aliasing numérico). Se conservará '{keep}' como representante; "
            f"los modelos {aliases_str} se omitirán del cuerpo principal "
            f"del informe por redundancia, sin pérdida de información empírica."
        )

    combined_clause = (
        "Nota de consolidación (MATH-07): " + " Asimismo, ".join(clauses) +
        " La elección entre modelos empíricamente equivalentes se hará, si procede, por coherencia teórica."
    )

    result.findings.append(Finding(
        severity="WARNING",
        check_id="MATH-07",
        message=(
            f"Redundancia numérica detectada en {len(redundant_groups)} grupos de modelos. "
            f"Generada cláusula de consolidación unificada."
        ),
        location="tabla 'Proyecciones Futuras'",
        correction=combined_clause,
    ))


def _check_math_08_narrative_vs_table(
    report_md: str,
    real_series: Optional[Dict[str, float]],
    result: ValidationResult,
) -> None:
    """
    MATH-08 — Reconciliación narrativa vs tabla.

    Extrae cifras numéricas del texto narrativo con regex
    (formatos 'N millones', 'N M', 'N.0 M') y las compara contra
    la serie histórica real. Reporta discrepancias de ±0.1-1M y genera
    una corrección estándar con la cifra correcta (la de la tabla).

    Excluye rangos del tipo "pasó de 15 a 23 millones" para evitar
    falsos positivos (las cifras de un rango no son valores anuales
    individuales).

    Determinista: no requiere LLM; es una reconciliación léxica simple.
    """
    if not real_series:
        return

    # Patrones de cifra en texto narrativo:
    #   "40.5 millones", "64,5 millones", "86.5 M", "alcanza los 35 millones"
    pattern = re.compile(
        r"(?:alcanza|alcanzar|alcanzaron|hacia los|"
        r"proyecta|proyectados?|de los|super[óo]|"
        r"rozar|pasa de|rondaron|rondando|"
        r"supera|sobre|paso a|saltaron|salto a|salto"
        r"|continu[óo] creciendo|continu[óo] creciendo|"
        r"adopción pasó de|adopción acumulada)\s+"
        r"(?:a los |hacia los |de los |los )?"
        r"(\d{1,3}(?:[.,]\d{1,2})?)\s*(?:millones(?:\s+de\s+usuarios)?|M\b)"
        r"|(\d{1,3}(?:[.,]\d{1,2})?)\s*M\b",
        re.IGNORECASE,
    )

    # Patrón de rango: "pasó de 15 a 23 millones", "de 15 a 23 M",
    # "pasó de 15 a 23 millones de usuarios"
    range_pattern = re.compile(
        r"(?:pas[oó]\s+)?de\s+"
        r"(\d{1,3}(?:[.,]\d{1,2})?)\s+a\s+"
        r"(\d{1,3}(?:[.,]\d{1,2})?)\s*"
        r"(?:millones(?:\s+de\s+usuarios)?|M\b)",
        re.IGNORECASE,
    )

    # Intentar asignar cada cifra del texto al año más probable
    # cercano por contexto de frase (heurística: el párrafo suele
    # mencionar un año o rango de años cerca).
    year_pattern = re.compile(
        r"(?:19|20)\d{2}(?:\s*[-–—]\s*(?:19|20)\d{2})?"
    )

    # Tolerancia: discrepancias superiores a 0.05 y menores a 5.0 M
    tol_low = 0.05
    tol_high = 5.0

    # Examinar párrafo a párrafo para acotar el contexto
    paragraphs = re.split(r"\n\s*\n", report_md)
    for para_idx, para in enumerate(paragraphs, start=1):
        # Saltar párrafos enteros de notas metodológicas
        if "nota metodol" in para.lower():
            continue

        # --- Excluir rangos: registrar posiciones de números que
        # --- son parte de un rango "de X a Y millones"
        range_spans: List[tuple] = []  # (start, end) en el párrafo
        for rm in range_pattern.finditer(para):
            range_spans.append((rm.start(), rm.end()))

        def in_range(pos: int) -> bool:
            for rs, re_ in range_spans:
                if rs <= pos < re_:
                    return True
            return False

        # localizar cifras en el párrafo
        for m in pattern.finditer(para):
            # saltar si esta cifra está dentro de un rango
            if in_range(m.start()):
                continue

            line_start = para.rfind("\n", 0, m.start()) + 1
            line_end = para.find("\n", m.start())
            if line_end == -1:
                line_end = len(para)
            line_text = para[line_start:line_end]

            if line_text.strip().startswith(("|", "*", "\\*", "_", ">")) or "nota metodol" in line_text.lower():
                continue

            raw = m.group(1) or m.group(2)
            if not raw:
                continue
            try:
                narrative_val = float(raw.replace(",", "."))
            except ValueError:
                continue

            # Obtener años específicos en esta línea
            years_in_line = year_pattern.findall(line_text)
            normalised_years_line: List[str] = []
            for y in years_in_line:
                if "-" in y or "–" in y or "—" in y:
                    last = re.findall(r"(?:19|20)\d{2}", y)
                    if last:
                        normalised_years_line.extend(last)
                else:
                    normalised_years_line.append(y)

            # Si el valor narrativo coincide perfectamente con alguno de los años en contexto, no es discrepancia
            context_years = normalised_years_line if normalised_years_line else normalised_years
            has_perfect_match = False
            for y_str in context_years:
                if y_str in real_series:
                    if abs(real_series[y_str] - narrative_val) <= tol_low:
                        has_perfect_match = True
                        break
            if has_perfect_match:
                continue

            # encontrar qué año de la serie está más cerca de la cifra
            # narrativa
            candidates: List[tuple] = []  # (diff, year, real)
            for y_str, real in real_series.items():
                diff = abs(real - narrative_val)
                if tol_low < diff <= tol_high:
                    candidates.append((diff, y_str, real))

            if not candidates:
                continue

            # si el párrafo menciona años, priorizar candidatos cuyos
            # años aparecen en el contexto
            years_to_use = normalised_years_line if normalised_years_line else normalised_years
            if years_to_use:
                prioritised = [
                    c for c in candidates if c[1] in years_to_use
                ]
                if prioritised:
                    candidates = prioritised

            # tomar el candidato con menor diferencia
            candidates.sort(key=lambda c: c[0])
            diff, year, real_val = candidates[0]

            # localizar línea exacta en el documento
            char_idx = report_md.find(para)
            line_no = report_md[:char_idx + para.find(m.group(0))].count(
                "\n"
            ) + 1

            result.findings.append(Finding(
                severity="WARNING",
                check_id="MATH-08",
                message=(
                    f"Cifra narrativa '{narrative_val}' (millones) "
                    f"discrepa de la tabla real para {year} "
                    f"(real={real_val} M, diff=+{diff:.2f} M). La "
                    f"autoridad es la tabla; el texto debe corregirse."
                ),
                location=(
                    f"párrafo {para_idx}, cerca de línea {line_no}"
                ),
                correction=(
                    f"Sustituir '{narrative_val} millones' por "
                    f"'{real_val:.1f} millones' (o '{real_val:.1f} M') "
                    f"para alinear con la serie histórica real."
                ),
            ))


def _check_math_09_rk_theoretical_clause(
    report_md: str,
    models_projections: Optional[Dict[str, Dict[str, float]]],
    result: ValidationResult,
) -> None:
    """
    MATH-09 — Cláusula estándar por elección teórica de R&K (o similar).

    Si el informe DESCARTA R&K (o cualquier modelo con mejor R²/MAPE
    que el modelo finalmente recomendado) apelando a 'sobreajuste', el
    informe DEBE declarar explicitamente que la elección del modelo
    ideal se hace 'por coherencia teórica, no por mejor ajuste empírico'.

    Detecta la presencia de esa cláusula estándar; si no existe, la
    genera lista para insertar.
    """
    if not models_projections:
        return

    # Buscar menciones de descarte de R&K / Logística por sobreajuste.
    # Normalizamos a minúsculas SIN acentos para tolerar ambas variantes.
    def _strip_accents(s: str) -> str:
        table = str.maketrans("áéíóúüñ", "aeiouun")
        return s.translate(table)

    low = _strip_accents(report_md.lower())
    discard_phrases = [
        "sobreajuste",
        "overfitting",
        "sobrestimacion",
        "subestima la friccion",
        "sobreajustado",
    ]
    mentions_rk_discard = (
        ("logistica" in low or "r&k" in low or "ryu & kim" in low or "ryu y kim" in low)
        and any(p in low for p in discard_phrases)
    )
    if not mentions_rk_discard:
        return

    # Comprobar si ya existe la cláusula estándar
    standard_clause_markers = [
        "por coherencia teorica",
        "no por mejor ajuste empirico",
        "no por su mejor ajuste",
        "eleccion teorica",
        "eleccion por criterio teorico",
        "la eleccion no se fundamenta en el mejor ajuste",
    ]
    already_present = any(m in low for m in standard_clause_markers)
    if already_present:
        return

    # Extraer dinámicamente R2 y MAPE de R&K
    rk_r2 = "0.9989"
    rk_mape = "2.16%"
    rk_row_pattern = re.compile(
        r"\|\s*Difusi[oó]n\s+Log[ií]stica\s*R&K\s*\|"
        r"\s*(\d+\.\d+)\s*\|\s*(\d+\.\d+)\s*%",
        re.IGNORECASE,
    )
    rk_match = rk_row_pattern.search(report_md)
    if rk_match:
        rk_r2 = rk_match.group(1)
        rk_mape = rk_match.group(2) + "%"

    # Extraer el modelo ideal recomendado en la sección de recomendación
    mappings = [
        ("Roset & Canals", ["dual market", "roset & canals", "roset y canals", "roset canals"]),
        ("Muller & Yogev", ["muller & yogev", "muller yogev"]),
        ("Van den Bulte & Joshi", ["van den bulte & joshi", "van den bulte joshi", "vdb & joshi"]),
        ("Fourt & Woodlock", ["fourt", "woodlock", "innovación pura"]),
        ("Gompertz", ["gompertz", "sigmoide asimétrica", "asimétrica"]),
        ("Generalized Bass", ["generalized bass", "bass generalizado", "gbm", "shocks de marketing", "precio"]),
        ("Horsky & Simon", ["horsky", "publicidad", "esfuerzo publicitario"]),
        ("Ladrón-de-Guevara & Putsis", ["ladrón-de-guevara", "ladrón de guevara", "ladron putsis", "ladron"]),
        ("Difusión Logística R&K", ["logístico", "logistic", "ryu & kim", "difusión logística", "logística", "logistica"]),
        ("Bass Clásico", ["bass clásico", "bass clasico", "bass estándar"]),
    ]
    
    def detect_recommended_model(text: str) -> str:
        sentences = re.split(r'[.\n]', text)
        target_sentences = []
        for s in sentences:
            s_lower = s.lower()
            if 'modelo' in s_lower and ('ideal' in s_lower or 'recomend' in s_lower or 'adopta' in s_lower):
                target_sentences.append(s)
                
        for s in target_sentences:
            for pretty_name, keywords in mappings:
                if any(kw in s.lower() for kw in keywords):
                    return pretty_name
                    
        for pretty_name, keywords in mappings:
            for kw in keywords:
                pos = text.lower().rfind(kw)
                if pos != -1:
                    return pretty_name
                
        return 'Dual Market (Roset & Canals)'

    recommended_model_name = detect_recommended_model(report_md)

    # Parsear todas las filas de la tabla para comparar R2/MAPE de R&K y modelo recomendado
    table_rows = re.findall(
        r"\|\s*([^\n|]+)\s*\|\s*(\d+\.\d+)\s*\|\s*(\d+\.\d+)\s*%",
        report_md
    )
    
    def _resolve_pretty_name(raw_name: str) -> str:
        for pretty_name, keywords in mappings:
            if any(kw in raw_name.lower() for kw in keywords):
                return pretty_name
        return raw_name

    resolved_rec = _resolve_pretty_name(recommended_model_name)
    rec_r2 = None
    rec_mape = None
    for name, r2_str, mape_str in table_rows:
        resolved_table = _resolve_pretty_name(name)
        if resolved_rec == resolved_table:
            try:
                rec_r2 = float(r2_str)
                rec_mape = float(mape_str)
            except ValueError:
                pass
            break

    rk_r2_val = None
    rk_mape_val = None
    for name, r2_str, mape_str in table_rows:
        if "r&k" in name.lower() or "logistica" in name.lower():
            try:
                rk_r2_val = float(r2_str)
                rk_mape_val = float(mape_str)
            except ValueError:
                pass
            break

    if rk_r2_val is not None and rec_r2 is not None:
        # Solo gatillar si R&K tiene estrictamente mejor ajuste empírico
        # (mejor R2 es mayor, mejor MAPE es menor)
        rk_better = (rk_r2_val > rec_r2) or (rk_mape_val < rec_mape)
        if not rk_better:
            return  # No se necesita cláusula si el modelo recomendado tiene igual o mejor ajuste


    clause = (
        f"Nota estándar (MATH-09): cuando se descarta un modelo con mejor "
        f"R²/MAPE que el modelo finalmente recomendado (p. ej. la "
        f"Difusión Logística R&K, con R²={rk_r2} y MAPE={rk_mape}, frente al "
        f"modelo elegido), el informe debe declarar explicitamente que "
        f"la elección se hace 'por coherencia teórica con la dinámica "
        f"del mercado, no por mejor ajuste empírico'. Por ejemplo: "
        f"\"La curva logística de R&K ofrece un mejor ajuste empírico que el "
        f"modelo elegido (R²={rk_r2}, MAPE={rk_mape}), pero su formulación no captura los "
        f"efectos de red entre productos complementarios del ecosistema. "
        f"Por coherencia teórica, no por mejor ajuste empírico, se adopta "
        f"como modelo ideal el de {recommended_model_name}.\""
    )

    result.findings.append(Finding(
        severity="WARNING",
        check_id="MATH-09",
        message=(
            "El informe descarta R&K / Logística por 'sobreajuste', "
            "pero no declara explicitamente que la elección del modelo "
            "ideal se hace por coherencia teórica, no por mejor ajuste "
            "empírico. Falta la cláusula estándar."
        ),
        location="sección 'Recomendación Científica y Modelo Ideal'",
        correction=clause,
    ))


# =========================================================================
# Checks de consistencia de notas (nuevos)
# =========================================================================

def _check_math_10_math09_consistency(
    report_md: str,
    result: ValidationResult,
) -> None:
    """
    MATH-10 — Consistencia de la nota MATH-09.

    Verifica que la nota MATH-09 insertada en el informe menciona:
      (a) el modelo R&K / Logística con los R² y MAPE correctos que
          aparecen en la tabla de ajuste del propio informe, y
      (b) el modelo recomendado correcto (el que el informe declara
          como "Modelo Ideal").

    Detecta copy-paste de notas de otros informes con modelo o cifras
    equivocadas (el crítico más frecuente en el pipeline).

    Caza dos tipos de error:
      1. La nota menciona un modelo ideal que no aparece como
         recomendado en la sección 5 del informe.
      2. La nota menciona R²/MAPE que no coinciden con los de R&K
         en la tabla de ajuste del informe.
    """
    low = report_md.lower()

    # --- 1. Localizar la nota MATH-09 ---
    math09_marker = "math-09"
    if math09_marker not in low:
        return  # no hay nota MATH-09, nada que validar

    # Extraer el bloque de la nota (entre el marcador y el siguiente **)
    idx = low.find(math09_marker)
    # buscar el cierre de la nota (siguiente '**' después del marcador)
    note_end = report_md.find("**", idx + len(math09_marker))
    if note_end == -1:
        note_end = idx + 500  # fallback: 500 chars
    note_text = report_md[idx:note_end]

    # --- 2. Extraer R² y MAPE de la nota ---
    # Patrones: "R²=0.9989", "R2=0.9989", "R²=0,9989"
    r2_pattern = re.compile(r"r[²2]\s*=\s*(\d+\.\d+)", re.IGNORECASE)
    mape_pattern = re.compile(r"mape\s*=\s*(\d+\.\d+)\s*%", re.IGNORECASE)

    note_r2_matches = r2_pattern.findall(note_text)
    note_mape_matches = mape_pattern.findall(note_text)

    # --- 3. Extraer R² y MAPE reales de R&K desde la tabla de ajuste ---
    # Buscar la fila "Difusión Logística R&K" en la tabla de ajuste
    rk_r2 = None
    rk_mape = None
    # Patrón de fila de tabla: | Difusión Logística R&K | 0.9999 | 1.12% |
    rk_row_pattern = re.compile(
        r"\|\s*Difusi[oó]n\s+Log[ií]stica\s*R&K\s*\|"
        r"\s*(\d+\.\d+)\s*\|\s*(\d+\.\d+)\s*%",
        re.IGNORECASE,
    )
    rk_match = rk_row_pattern.search(report_md)
    if rk_match:
        rk_r2 = rk_match.group(1)
        rk_mape = rk_match.group(2)

    # --- 4. Comparar R² de la nota vs R² de la tabla ---
    if note_r2_matches and rk_r2:
        note_r2 = note_r2_matches[0]
        if abs(float(note_r2) - float(rk_r2)) > 0.0001:
            result.findings.append(Finding(
                severity="CRITICAL",
                check_id="MATH-10",
                message=(
                    f"La nota MATH-09 menciona R²={note_r2} para R&K, "
                    f"pero la tabla de ajuste del informe dice "
                    f"R²={rk_r2}. La nota parece copiada de otro "
                    f"informe con cifras distintas."
                ),
                location="nota MATH-09",
                correction=(
                    f"Sustituir R²={note_r2} por R²={rk_r2} en la "
                    f"nota MATH-09."
                ),
            ))

    # --- 5. Comparar MAPE de la nota vs MAPE de la tabla ---
    if note_mape_matches and rk_mape:
        note_mape = note_mape_matches[0]
        if abs(float(note_mape) - float(rk_mape)) > 0.05:
            result.findings.append(Finding(
                severity="CRITICAL",
                check_id="MATH-10",
                message=(
                    f"La nota MATH-09 menciona MAPE={note_mape}% para "
                    f"R&K, pero la tabla de ajuste del informe dice "
                    f"MAPE={rk_mape}%. La nota parece copiada de otro "
                    f"informe."
                ),
                location="nota MATH-09",
                correction=(
                    f"Sustituir MAPE={note_mape}% por MAPE={rk_mape}% "
                    f"en la nota MATH-09."
                ),
            ))

    # --- 6. Verificar que el modelo ideal de la nota coincide con sección 5 ---
    ideal_pattern = re.compile(
        r"(?:se adopta como modelo ideal el de|"
        r"modelo ideal el de)\s+(.+?)(?:\.\s|\.\s*$|\*\*)",
        re.IGNORECASE,
    )
    ideal_match = ideal_pattern.search(note_text)
    if ideal_match:
        note_ideal = ideal_match.group(1).strip().rstrip(".**")

        # Buscar en sección 5 qué modelo se declara como ideal
        sec5_pattern = re.compile(
            r"Modelo Ideal de Difusión para\s+\w+\s+es el\s+(.+?)(?:\*\*|\(|\n)",
            re.IGNORECASE,
        )
        sec5_match = sec5_pattern.search(report_md)
        if sec5_match:
            sec5_ideal = sec5_match.group(1).strip()
            def _norm(s):
                return re.sub(r"[\s\*\(\).,\"\']+", " ", s).strip().lower()
            norm_note = _norm(note_ideal)
            norm_sec5 = _norm(sec5_ideal)
            # Use bidirectional substring containment: the note may use a shorter name
            # (e.g. "Ladrón-de-Guevara & Putsis") while sec5 uses the full formal name
            # ("Modelo de Mercado Dinámico de Ladrón-de-Guevara & Putsis").
            # A mismatch only fires if neither is a substring of the other.
            models_match = (
                norm_note == norm_sec5
                or norm_note in norm_sec5
                or norm_sec5 in norm_note
            )
            if not models_match:
                result.findings.append(Finding(
                    severity="CRITICAL",
                    check_id="MATH-10",
                    message=(
                        f"La nota MATH-09 declara como modelo ideal "
                        f"'{note_ideal}', pero la sección 5 del "
                        f"informe declara '{sec5_ideal}'. La nota "
                        f"parece copiada de otro informe con un "
                        f"modelo recomendado distinto."
                    ),
                    location="nota MATH-09 vs sección 5",
                    correction=(
                        f"Sustituir '{note_ideal}' por "
                        f"'{sec5_ideal}' en la nota MATH-09."
                    ),
                ))


def _check_math_11_math07_completeness(
    report_md: str,
    models_projections: Optional[Dict[str, Dict[str, float]]],
    result: ValidationResult,
) -> None:
    """
    MATH-11 — Completitud de la nota MATH-07.

    Verifica que la nota MATH-07 declara TODOS los grupos de modelos
    alias detectados (no solo el primero). Si hay múltiples grupos
    con predicciones idénticas y la nota solo menciona uno, es un
    copy-paste incompleto.
    """
    if not models_projections or len(models_projections) < 2:
        return

    low = report_md.lower()

    # --- 1. Localizar la nota MATH-07 ---
    math07_marker = "math-07"
    if math07_marker not in low:
        return  # no hay nota MATH-07

    idx = low.find(math07_marker)
    # buscar el cierre de la nota
    note_end = report_md.find("**", idx + len(math07_marker))
    if note_end == -1:
        note_end = idx + 800
    note_text_low = low[idx:note_end]

    # --- 2. Recalcular grupos alias ---
    def signature(proj):
        return tuple(round(v, 2) for _, v in sorted(proj.items()))

    sig_map: Dict[tuple, List[str]] = {}
    for model, proj in models_projections.items():
        sig = signature(proj)
        sig_map.setdefault(sig, []).append(model)

    alias_groups = [g for g in sig_map.values() if len(g) > 1]

    if not alias_groups:
        return

    # --- 3. Verificar que cada grupo está mencionado en la nota ---
    for group in alias_groups:
        # al menos 2 modelos del grupo deben aparecer en la nota
        mentioned = sum(1 for m in group if m.lower() in note_text_low)
        if mentioned < 2:
            mentioned_short = 0
            for m in group:
                short = m.lower()[:15]
                if short in note_text_low:
                    mentioned_short += 1
            if mentioned_short < 2:
                result.findings.append(Finding(
                    severity="CRITICAL",
                    check_id="MATH-11",
                    message=(
                        f"Grupo alias no declarado en la nota MATH-07: "
                        f"{', '.join(group)} (predicciones idénticas "
                        f"a 2 decimales). La nota solo declara uno de "
                        f"los múltiples grupos con aliasing detectados."
                    ),
                    location="nota MATH-07",
                    correction=(
                        f"Añadir a la nota MATH-07: 'los modelos "
                        f"{', '.join(group)} presentan predicciones "
                        f"numéricamente indistinguibles (aliasing). "
                        f"Se conservará '{group[0]}' como representante.'"
                    ),
                ))


def _check_math_12_consensus_monotonicity(
    report_md: str,
    result: ValidationResult,
) -> None:
    """
    MATH-12 — Verifica la monotonía no decreciente de las proyecciones de consenso
    extraídas del reporte de texto. Si la proyección para 2030 es mayor que 2035,
    indica una inconsistencia física (crecimiento negativo en curva acumulada).
    """
    import statistics
    
    values: Dict[int, List[float]] = {}
    lines = report_md.splitlines()
    for line in lines:
        line_lower = line.lower()
        stripped = line_lower.strip()
        if not (stripped.startswith('*') or stripped.startswith('-') or (stripped and stripped[0].isdigit())):
            continue
            
        # Omitir frases con comparativas de múltiples años
        years_on_line = list(set(re.findall(r'\b(20[2-5]\d)\b', line_lower)))
        if len(years_on_line) != 1:
            continue
            
        year = int(years_on_line[0])
        if year not in [2030, 2035]:
            continue
            
        # Omitir palabras de incremento
        if any(w in line_lower for w in ["crecimiento", "incremento", "otros", "adicionales", "aumento", "diferencia"]):
            continue
            
        ranges = list(re.finditer(r'([\d.,]+)\s*(?:a|-|—)\s*([\d.,]+)\s*millones?', line_lower))
        singles = list(re.finditer(r'([\d.,]+)\s*millones?', line_lower))
        
        val: Optional[float] = None
        if ranges:
            try:
                v1 = float(ranges[0].group(1).replace(',', '.'))
                v2 = float(ranges[0].group(2).replace(',', '.'))
                # Prevent extracting years as range values
                if not ((1900 <= v1 <= 2100) or (1900 <= v2 <= 2100)):
                    val = (v1 + v2) / 2.0
            except ValueError:
                pass
        elif singles:
            is_in_range = any(r.start() <= singles[0].start() <= r.end() for r in ranges)
            if not is_in_range:
                try:
                    val = float(singles[0].group(1).replace(',', '.'))
                except ValueError:
                    pass
                    
        if val is not None:
            if year not in values:
                values[year] = []
            values[year].append(val)
            
    mid_2030 = statistics.median(values[2030]) if 2030 in values and values[2030] else None
    mid_2035 = statistics.median(values[2035]) if 2035 in values and values[2035] else None
    
    if mid_2030 is not None and mid_2035 is not None:
        if mid_2030 > mid_2035:
            result.findings.append(Finding(
                severity="CRITICAL",
                check_id="MATH-12",
                message=(
                    f"Curva de consenso matemáticamente inválida: la adopción acumulada "
                    f"proyectada para 2030 ({mid_2030:.2f} M) es superior a la de 2035 ({mid_2035:.2f} M). "
                    f"Las proyecciones acumulativas deben ser no decrecientes."
                ),
                location="Sección 2 / Sección 4 (Pronóstico de Consenso)",
                correction=(
                    f"Ajustar los valores del consenso en el informe de modo que la proyección "
                    f"para 2035 sea mayor o igual a {mid_2030:.2f} M (valor de 2030)."
                )
            ))


def _check_math_13_infancy_growth_ceiling(
    report_md: str,
    real_series: Optional[Dict[str, float]],
    result: ValidationResult,
) -> None:
    """
    MATH-13 — Verifica que el crecimiento proyectado a 5 y 10 años para tecnologías
    en etapa de lanzamiento (nacientes) sea matemáticamente realista y acotado.
    Si la base instalada actual es pequeña (< 5M) o hay muy pocos datos reales (>0),
    evita que el consenso declare proyecciones explosivas absurdas.
    """
    if not real_series:
        return
        
    vals = [float(v) for v in real_series.values() if v is not None]
    if not vals:
        return
        
    m_max = max(vals)
    n_nonzero = sum(1 for v in vals if v > 0.0)
    
    # Definir el techo de crecimiento razonable en base a la madurez
    limit = None
    if n_nonzero <= 2:
        limit = 5.0 * m_max
    elif m_max < 5.0:
        limit = 15.0 * m_max
        
    if limit is None:
        return
        
    # Extraer valores del reporte
    import statistics
    values: Dict[int, List[float]] = {}
    lines = report_md.splitlines()
    for line in lines:
        line_lower = line.lower()
        stripped = line_lower.strip()
        if not (stripped.startswith('*') or stripped.startswith('-') or (stripped and stripped[0].isdigit())):
            continue
            
        years_on_line = list(set(re.findall(r'\b(20[2-5]\d)\b', line_lower)))
        if len(years_on_line) != 1:
            continue
            
        year = int(years_on_line[0])
        if year not in [2030, 2035]:
            continue
            
        if any(w in line_lower for w in ["crecimiento", "incremento", "otros", "adicionales", "aumento", "diferencia"]):
            continue
            
        ranges = list(re.finditer(r'([\d.,]+)\s*(?:a|-|—)\s*([\d.,]+)\s*millones?', line_lower))
        singles = list(re.finditer(r'([\d.,]+)\s*millones?', line_lower))
        
        val: Optional[float] = None
        if ranges:
            try:
                v1 = float(ranges[0].group(1).replace(',', '.'))
                v2 = float(ranges[0].group(2).replace(',', '.'))
                # Prevent extracting years as range values
                if not ((1900 <= v1 <= 2100) or (1900 <= v2 <= 2100)):
                    val = (v1 + v2) / 2.0
            except ValueError:
                pass
        elif singles:
            is_in_range = any(r.start() <= singles[0].start() <= r.end() for r in ranges)
            if not is_in_range:
                try:
                    val = float(singles[0].group(1).replace(',', '.'))
                except ValueError:
                    pass
                    
        if val is not None:
            if year not in values:
                values[year] = []
            values[year].append(val)
            
    mid_2030 = statistics.median(values[2030]) if 2030 in values and values[2030] else None
    mid_2035 = statistics.median(values[2035]) if 2035 in values and values[2035] else None
    
    # Comprobar contra el límite
    for yr, mid_val in [(2030, mid_2030), (2035, mid_2035)]:
        if mid_val is not None and mid_val > limit:
            result.findings.append(Finding(
                severity="CRITICAL",
                check_id="MATH-13",
                message=(
                    f"Crecimiento de consenso irreal para tecnología naciente: la adopción de consenso "
                    f"estimada para {yr} ({mid_val:.2f} M) supera el límite de seguridad matemática "
                    f"({limit:.2f} M, correspondiente a {limit/m_max:.1f}x el máximo histórico de {m_max:.2f} M). "
                    f"Para tecnologías en su infancia, las proyecciones a largo plazo deben estar acotadas."
                ),
                location="Sección 2 / Sección 4 (Pronóstico de Consenso)",
                correction=(
                    f"Ajustar el modelo operativo o consenso del informe para recomendar un modelo "
                    f"más conservador (por ejemplo, Ryu & Kim o Muller & Yogev) de modo que las proyecciones "
                    f"para {yr} no superen los {limit:.2f} M."
                )
            ))


def _check_math_14_geopopulation_sanity_check(
    report_md: str,
    technology: str,
    real_series: Optional[Dict[str, float]],
    result: ValidationResult,
) -> None:
    """
    MATH-14 — Realiza un sanity check geodemográfico para evitar la mezcla accidental
    de datos de escala global en informes con alcance local/regional.
    """
    if not real_series:
        return
        
    vals = [float(v) for v in real_series.values() if v is not None]
    if not vals:
        return
        
    m_max = max(vals)
    tech_lower = technology.lower()
    
    # Base de datos demográfica de regiones comunes usando raíces robustas a codificación
    country_populations = {
        "norue": (5.5, "Noruega"),
        "norwa": (5.5, "Noruega"),
        "espa": (48.0, "España"),
        "spai": (48.0, "España"),
        "portu": (10.3, "Portugal"),
        "alema": (84.0, "Alemania"),
        "germa": (84.0, "Alemania"),
        "franc": (68.0, "Francia"),
        "ital": (59.0, "Italia"),
        "reino unid": (67.0, "Reino Unido"),
        "united king": (67.0, "Reino Unido"),
        "uk": (67.0, "Reino Unido"),
        "suec": (10.5, "Suecia"),
        "swed": (10.5, "Suecia"),
        "finlan": (5.6, "Finlandia"),
        "dinamarc": (5.9, "Dinamarca"),
        "denmar": (5.9, "Dinamarca"),
        "suiz": (8.9, "Suiza"),
        "switzer": (8.9, "Suiza"),
    }
    
    # Normalización agresiva
    def clean_str(s):
        s = s.lower().replace("ñ", "n").replace("", "")
        return re.sub(r"[^a-z0-9\s]", "", s)
        
    tech_clean = clean_str(technology)
    
    matched_region = None
    matched_pop = None
    for stem, (pop, name) in country_populations.items():
        if clean_str(stem) in tech_clean:
            matched_region = name
            matched_pop = pop
            break
            
    if matched_region is None or matched_pop is None:
        return
        
    # Un mercado real regional de usuarios/dispositivos (excluyendo microprocesadores o vacunas multicomponente)
    # no puede superar físicamente a la población local multiplicada por un factor de seguridad de 1.2.
    limit_cap = matched_pop * 1.2
    
    # Comprobar el máximo histórico
    if m_max > limit_cap:
        result.findings.append(Finding(
            severity="CRITICAL",
            check_id="MATH-14",
            message=(
                f"Sanity check geodemográfico fallido: los datos históricos muestran una adopción "
                f"máxima de {m_max:.2f} M, lo cual supera el límite físicamente posible para la región "
                f"'{matched_region.title()}' (población total de {matched_pop:.2f} M). Esto indica que se han "
                f"importado accidentalmente datos mundiales/globales en lugar de datos locales de Noruega/región."
            ),
            location="Sección 2 (Datos Históricos)",
            correction=(
                f"Filtrar y reemplazar la serie temporal histórica para usar exclusivamente datos locales "
                f"del mercado de {matched_region.title()} y asegurar que las cifras no superen el límite de {limit_cap:.2f} M."
            )
        ))
        return

    # Extraer y comprobar también las proyecciones de consenso de la narrativa
    import statistics
    values: Dict[int, List[float]] = {}
    for line in report_md.splitlines():
        line_lower = line.lower()
        stripped = line_lower.strip()
        if not (stripped.startswith('*') or stripped.startswith('-') or (stripped and stripped[0].isdigit())):
            continue
            
        years_on_line = list(set(re.findall(r'\b(20[2-5]\d)\b', line_lower)))
        if len(years_on_line) != 1:
            continue
            
        year = int(years_on_line[0])
        if year not in [2030, 2035]:
            continue
            
        if any(w in line_lower for w in ["crecimiento", "incremento", "otros", "adicionales", "aumento", "diferencia"]):
            continue
            
        ranges = list(re.finditer(r'([\d.,]+)\s*(?:a|-|—)\s*([\d.,]+)\s*millones?', line_lower))
        singles = list(re.finditer(r'([\d.,]+)\s*millones?', line_lower))
        
        val: Optional[float] = None
        if ranges:
            try:
                v1 = float(ranges[0].group(1).replace(',', '.'))
                v2 = float(ranges[0].group(2).replace(',', '.'))
                # Prevent extracting years as range values
                if not ((1900 <= v1 <= 2100) or (1900 <= v2 <= 2100)):
                    val = (v1 + v2) / 2.0
            except ValueError:
                pass
        elif singles:
            is_in_range = any(r.start() <= singles[0].start() <= r.end() for r in ranges)
            if not is_in_range:
                try:
                    val = float(singles[0].group(1).replace(',', '.'))
                except ValueError:
                    pass
                    
        if val is not None:
            if year not in values:
                values[year] = []
            values[year].append(val)
            
    mid_2030 = statistics.median(values[2030]) if 2030 in values and values[2030] else None
    mid_2035 = statistics.median(values[2035]) if 2035 in values and values[2035] else None
    
    for yr, mid_val in [(2030, mid_2030), (2035, mid_2035)]:
        if mid_val is not None and mid_val > limit_cap:
            result.findings.append(Finding(
                severity="CRITICAL",
                check_id="MATH-14",
                message=(
                    f"Sanity check geodemográfico fallido: la proyección de consenso para {yr} "
                    f"({mid_val:.2f} M) supera el límite físicamente posible para la región '{matched_region.title()}' "
                    f"(población de {matched_pop:.2f} M). Por favor, asegúrate de restringir la escala."
                ),
                location="Sección 5 (Pronóstico de Consenso)",
                correction=(
                    f"Ajustar el informe y las proyecciones de consenso para la región de {matched_region.title()} "
                    f"de modo que no superen el límite demográfico de {limit_cap:.2f} M."
                )
            ))


# =========================================================================
# CLI mínimo para pruebas
# =========================================================================

if __name__ == "__main__":
    import argparse
    import json
    import sys

    p = argparse.ArgumentParser(
        description="Validador determinístico de informes de adopción."
    )
    p.add_argument(
        "--report", required=True,
        help="Ruta al fichero Markdown del informe."
    )
    p.add_argument(
        "--technology", required=True,
        help="Nombre de la tecnología (ej. Grifols, Gemini)."
    )
    p.add_argument(
        "--launch-year", type=int, required=True,
        help="Año de lanzamiento comercial del producto."
    )
    p.add_argument(
        "--real-series", default="{}",
        help="JSON con la serie real: {\"2015\": 1.0, ...}"
    )
    p.add_argument(
        "--projections", default="{}",
        help="JSON con proyecciones por modelo."
    )
    p.add_argument(
        "--consensus", default="{}",
        help="JSON con pronóstico de consenso."
    )
    args = p.parse_args()

    with open(args.report, encoding="utf-8") as f:
        md = f.read()

    findings = validate_report(
        report_md=md,
        technology=args.technology,
        launch_year=args.launch_year,
        real_series=json.loads(args.real_series) if args.real_series else None,
        models_projections=(
            json.loads(args.projections) if args.projections else None
        ),
        consensus=json.loads(args.consensus) if args.consensus else None,
    )

    print(findings.summary())
    print()
    for f in findings.findings:
        print(f"[{f.severity}] {f.check_id} — {f.message}")
        if f.location:
            print(f"    ubicación: {f.location}")
        if f.correction:
            print(f"    corrección: {f.correction}")
        print()

    sys.exit(0 if not findings.has_critical else 1)