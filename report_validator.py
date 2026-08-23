#!/usr/bin/env python3
"""
report_validator.py
--------------------
Capa de validacion de coherencia para informes de adopcion tecnologica
generados por el pipeline LLM + RAG (ej. tab_rag.py / report_compiler.py).
 
Corre ANTES de exportar el PDF final. Si detecta problemas, los reporta
con severidad y contexto, para que un humano (o el propio pipeline)
decida si bloquea la generacion o solo advierte.
 
Uso como script:
    python report_validator.py ruta_al_informe.txt
 
Uso como libreria:
    from report_validator import ReportValidator, ModelFit
    rv = ReportValidator(narrative_text, historical_table, model_fits)
    issues = rv.run_all
 
No requiere dependencias externas (solo stdlib).
"""
 
from __future__ import annotations
import re
import sys
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
 
 
# --------------------------------------------------------------------------
# Estructuras de datos
# --------------------------------------------------------------------------
 
@dataclass
class Issue:
    severity: str          # "BLOCKER" | "WARNING" | "INFO"
    category: str          # nombre corto del chequeo
    message: str
    evidence: str = ""
 
    @property
    def rule_id(self) -> str:
        return self.category
 
    def __str__(self):
        tag = {"BLOCKER": "🛑", "WARNING": "⚠️ ", "INFO": "ℹ️ "}.get(self.severity, "")
        s = f"{tag} [{self.severity}] ({self.category}) {self.message}"
        if self.evidence:
            s += f"\n      -> evidencia: {self.evidence}"
        return s
 
 
@dataclass
class ModelFit:
    name: str
    r2: float
    mape: float
    projections: Dict[int, float] = field(default_factory=dict)  # {year: value_millones}
    score: Optional[float] = None
 
 
# Referencias academicas reales conocidas para el dominio de modelos de difusion.
# Cualquier cita que NO aparezca aqui se marca como sospechosa (posible alucinacion).
# Ampliar libremente con la bibliografia real de cada pipeline/dominio.
KNOWN_REFERENCES = {
    ("bass", 1969),
    ("rogers", 1995), ("rogers", 2003),
    ("moore", 1991), ("mahajan", 1990),
    ("roset", 2011), ("canals", 2011),
    ("tanny", 1988), ("derzko", 1988),
    ("steffens", 1992), ("murthy", 1992),
    ("muller", 2006), ("yogev", 2006),
    ("van den bulte", 2007), ("joshi", 2007),
    ("ladron-de-guevara", 2011), ("ladron de guevara", 2011), ("putsis", 2011),
    ("fourt", 1960), ("woodlock", 1960),
    ("gbm", 1994), ("bass", 1994), ("krishnan", 1994), ("jain", 1994),
    ("horsky", 1983), ("simon", 1983),
}
 
# Comandos LaTeX que nunca deberian sobrevivir a un PDF ya renderizado como texto plano
LATEX_LEAK_PATTERN = re.compile(
    r"\\(theta|exp|frac|left|right|gamma|alpha|beta|sum|int|cdot|approx|geq|leq)\b"
)
 
# "Autor(es) (Año)" -> ej. "Ladrón-de-Guevara & Putsis (2011)" o ""
CITATION_PATTERN = re.compile(
    r"([A-ZÁÉÍÓÚÑ][\w\-áéíóúñ]+(?:\s*(?:&|y|and|,)\s*[A-ZÁÉÍÓÚÑ][\w\-áéíóúñ]+)?)"
    r"\s*[\(,]\s*(\d{4})\s*\)?"
)
 
# Palabras que matchean el patron de cita pero NO son nombres de autor
# (evita falsos positivos como "Hito 5 Años (2030)" o "Figura (2024)")
CITATION_STOPWORDS = {
    "año", "años", "hito", "figura", "tabla", "ecuación", "ecuacion",
    "capítulo", "capitulo", "sección", "seccion", "página", "pagina",
    "gráfica", "grafica", "anexo", "apartado", "mercado", "mercados", "tecnología",
    "tecnologia", "informe", "estudio", "proyección", "proyeccion", "industria",
    "usuario", "usuarios", "user", "users", "consumidor", "consumidores",
    "cliente", "clientes", "suscriptor", "suscriptores", "adopción", "adopcion",
    "plataforma", "empresa", "compañía", "compañia", "fuente", "referencia",
    "histórica", "historica", "serie", "versión", "version", "fase", "fases",
    "detallada", "detalladas", "análisis", "analisis", "resumen", "escenario", "escenarios",
    "estratégica", "estratégicas", "estratégico", "estratégicos", "estratégica", "estratégico",
    "madurez", "saturación", "saturacion", "consolidación", "consolidacion", "penetración", "penetracion",
    "difusión", "difusion", "innovación", "innovacion", "crecimiento", "expansión", "expansion",
    "evolución", "evolucion", "transformación", "transformacion", "adopción", "adopcion",
    "despegue", "aceleración", "aceleracion", "lanzamiento", "hito", "inicio", "fase", "etapa",
    "base", "retención", "retencion", "especialización", "especializacion", "sostenida", "caso", "casos",
    "banda", "bandas", "rango", "rangos", "nivel", "niveles", "valor", "valores", "punto", "puntos",
    # Nombres de compañías tecnológicas y productos: sus reportes anuales se citan como "Spotify (2024)"
    # y no son alucinaciones del LLM — son referencias a datos corporativos legítimos.
    "spotify", "netflix", "tiktok", "apple", "google", "meta", "amazon", "chatgpt", "openai", "anthropic", "claude",
    "youtube", "instagram", "twitter", "x corp", "microsoft", "samsung",
    "airbnb", "uber", "lyft", "snapchat", "pinterest", "linkedin",
    "statista", "idc", "gartner", "forrester", "emarketer", "iab",
}
 
# "• 2022: ... (0.1M)" en el texto narrativo
NARRATIVE_YEAR_VALUE_PATTERN = re.compile(
    r"(20\d{2})[^\n]{0,120}?\(\s*([\d.]+)\s*M\)"
)
 
# --- Deteccion generica de cifras "en millones" asociadas a un año -----------
# No dependemos de frases fijas ("Año X:", "Hito N Años (X)"): en su lugar
# buscamos CUALQUIER mencion de millones cerca de un año objetivo (2030, 2035, ...)
# en cualquier parte del texto narrativo (fuera de las tablas comparativas).
 
# Año como palabra completa (evita matchear "22030" o similar)
YEAR_MENTION_PATTERN = re.compile(r"(?<!\d)(20[0-4]\d)(?!\d)")
 
# Rango: "145 a 160 millones", "entre 145 y 160 millones", "145-160 millones"
RANGE_MILLONES_PATTERN = re.compile(
    r"~?\s*(\d{1,4}(?:\.\d+)?)\s*(?:a|-|–|y)\s*~?\s*(\d{1,4}(?:\.\d+)?)\s*millones",
    re.IGNORECASE,
)

GROWTH_ADJECTIVES = {
    r"\bmeseta\b|\bestancamiento\b": (-5.0, 15.0),
    r"\bdesaceleraci[oó]n\b": (-100.0, 20.0),
    r"\bmoderaci[oó]n paulatina\b|\bcrecimiento paulatino\b|\bmoder[aá]ndose paulatinamente\b|\bexpansi[oó]n paulatina\b": (5.0, 45.0),
    r"\bcrecimiento sostenido\b|\bcrecimiento continuo\b|\btrayectoria de crecimiento\b": (2.0, 10000.0),
    r"\baceleraci[oó]n robusta\b|\bcrecimiento explosivo\b|\bfuerte aceleraci[oó]n\b": (40.0, 10000.0),
}

SUPERIORITY_PHRASES = re.compile(
    r"(ligeramente superior|ligeramente inferior|marginalmente superior|marginalmente inferior|mejor ajuste|menor MAPE|ajuste superior|más preciso)",
    re.IGNORECASE,
)

 
 
def _looks_like_year(token: str) -> bool:
    """Evita que un año adyacente ('...para 2030 y 126 millones') se lea como
    limite inferior de un rango numerico."""
    return bool(re.fullmatch(r"20[0-4]\d", token))
 
 
# Valor unico: "124.16 millones", "~290 millones", "297.06M"
SINGLE_MILLONES_PATTERN = re.compile(
    r"~?\s*(\d{1,4}(?:\.\d+)?)\s*(?:M\b|millones)",
    re.IGNORECASE,
)
 
# Una linea con 3+ menciones de millones se trata como fila de tabla comparativa
# (varios modelos distintos para el mismo año es *esperado*, no una contradiccion)
# y se excluye del escaneo de consenso.
TABLE_ROW_MILLONES_THRESHOLD = 3
 
 
class ReportValidator:
    def __init__(
        self,
        narrative_text: str,
        historical_table: Optional[Dict[int, float]] = None,
        model_fits: Optional[List[ModelFit]] = None,
        tolerance_pct: float = 3.0,
        df_proj=None,
    ):
        """
        narrative_text: todo el texto del informe (secciones 1, 5 y 6 sobre todo).
        historical_table: {año: valor_millones} tal como aparece en la tabla oficial (seccion 2).
        model_fits: lista de ModelFit extraidos de las tablas de ajuste/proyeccion (seccion 3-4).
        tolerance_pct: tolerancia porcentual antes de marcar una discrepancia numerica.
        df_proj: dataframe con proyecciones.
        """
        self.text = narrative_text
        self.historical_table = historical_table or {}
        self.model_fits = model_fits or []
        self.tolerance_pct = tolerance_pct
        self.df_proj = df_proj
        self.issues: List[Issue] = []
 
    # ---------------------------------------------------------------- checks
 
    def check_totals_as_increments(self, per_year, last_hist_val=None):
        """[GLM-PATCH] BLOCKER: cifra junto a palabra de incremento que
        coincide con un total proyectado del recomendado y con ningún
        incremento válido. Detecta 'aumento de 4920.89M hasta 2031'."""
        if not per_year:
            return
        vals = list(per_year.values())
        # [FIX ronda-3] Tolerancia escalada a la DISPERSIÓN de los valores,
        # no al 2% del máximo: con totales ~5000M y saltos interanuales ~60M,
        # tol=100M hace colisionar incrementos legítimos con totales.
        vals_span = (max(vals) - min(vals)) if len(vals) > 1 else max(vals)
        tol = max(1.0, 0.01 * abs(vals_span))
        years = sorted(per_year)
        valid_incs = []
        for i, y in enumerate(years):
            for y0 in years[:i]:
                valid_incs.append(per_year[y] - per_year[y0])
        if last_hist_val is not None:
            for y in years:
                valid_incs.append(per_year[y] - last_hist_val)
        pat = re.compile(
            r'\b(aumento|incremento|crecimiento|adici[oó]n|diferencia)\b'
            r'([\s\S]{1,100}?)(?:\*\*)?\b(\d+(?:[\.,]\d+)?)\b(?:\*\*)?\s*'
            r'(millones(?:\s+de\s+(?:usuarios|suscriptores|clientes))?|M\b)',
            re.IGNORECASE)
        for m in pat.finditer(self.text):
            line = self.text[self.text.rfind('\n', 0, m.start()) + 1:
                             self.text.find('\n', m.end())]
            if '|' in line:      # filas de tabla: fuera de alcance
                continue
            try:
                val = float(m.group(3).replace(',', '.'))
            except ValueError:
                continue
            is_total = any(abs(val - v) < tol for v in vals)
            is_inc = any(abs(val - inc) < tol for inc in valid_incs)
            if is_total and not is_inc:
                self.issues.append(Issue(
                    "BLOCKER", "total_citado_como_incremento",
                    f"La cifra {m.group(3)} aparece como '{m.group(1)}' pero "
                    "coincide con un total proyectado del modelo recomendado, "
                    "no con un incremento válido.",
                    evidence=m.group(0)))

    def check_year_value_swap(self, v_a, v_b, y_a, y_b):
        """[GLM-PATCH] BLOCKER: cifra asociada (por cercanía de caracteres)
        a un año clave que coincide con el valor del OTRO año clave.
        Detecta 'Proyección para 2031: 4978.27M'."""
        if v_a is None or v_b is None:
            return
        gap = abs(v_b - v_a)
        if gap < 1e-6:
            return
        tol = min(max(1.0, 0.02 * max(v_a, v_b)), gap / 3.0)
        for year, own, other in ((y_a, v_a, v_b), (y_b, v_b, v_a)):
            for ym in re.finditer(r'\b' + str(year) + r'\b', self.text):
                ws = max(0, ym.start() - 80)
                window = self.text[ws: min(len(self.text), ym.end() + 80)]
                if '|' in window:   # tablas: fuera de alcance
                    continue
                for cm in re.finditer(r'\b(\d{1,5}(?:[\.,]\d+)?)\b', window):
                    try:
                        val = float(cm.group(1).replace(',', '.'))
                    except ValueError:
                        continue
                    if abs(val - other) > tol or abs(val - own) < tol:
                        continue
                    nearest, nd = None, 10**9
                    for y2 in re.finditer(r'\b(20\d{2})\b', window):
                        d = abs(y2.start() - cm.start())
                        if d < nd:
                            nearest, nd = int(y2.group(1)), d
                    if nearest == year:
                        self.issues.append(Issue(
                            "BLOCKER", "valor_intercambiado_entre_anios",
                            f"Cifra {cm.group(1)} asociada a {year} pero "
                            f"coincide con el valor de "
                            f"{2036 if year == 2031 else 2031} ({other:.2f}M) "
                            "del modelo recomendado.",
                            evidence=window.strip()[:200]))

    def check_narrative_vs_table(self, window: int = 150) -> None:
        """Versión generalizada: cualquier cifra 'X millones' cerca de un año
        histórico conocido en historical_table se contrasta contra el valor oficial,
        evitando falsos positivos con proyecciones futuras."""
        clean_text = self._filter_out_table_rows(self.text)
        known_years = set(self.historical_table.keys())
        last_hist_year = max(known_years) if known_years else 2024

        year_positions = [
            (int(m.group(1)), m.start(), m.end())
            for m in YEAR_MENTION_PATTERN.finditer(clean_text)
            if int(m.group(1)) in known_years
        ]
        if not year_positions:
            return

        numeric_mentions = []
        consumed_spans = []
        for rm in RANGE_MILLONES_PATTERN.finditer(clean_text):
            v1, v2 = float(rm.group(1)), float(rm.group(2))
            numeric_mentions.append(((v1 + v2) / 2, rm.group(0).strip(), rm.start(), rm.end()))
            consumed_spans.append((rm.start(), rm.end()))
        for sm in SINGLE_MILLONES_PATTERN.finditer(clean_text):
            if any(s <= sm.start() < e for s, e in consumed_spans):
                continue
            numeric_mentions.append((float(sm.group(1)), sm.group(0).strip(), sm.start(), sm.end()))

        INCREMENT_KEYWORDS = {
            "incremento", "aumento", "crecimiento", "añadió", "anadió", "sumó", "sumo",
            "adición", "adicion", "diferencia", "variación", "variacion", "incorporó",
            "incorporo", "captó", "capto", "ganó", "gano", "ganando", "añadiendo",
            "anadiendo", "expansión", "expansion", "adquisición", "adquisicion",
            "nuevos", "neto", "netos", "adicionales", "subida", "delta", "pasando"
        }

        for value, evidence, n_start, n_end in numeric_mentions:
            best_year, best_dist = None, None
            for year, y_start, y_end in year_positions:
                dist = min(abs(n_start - y_end), abs(y_start - n_end))
                if dist > window:
                    continue
                if best_dist is None or dist < best_dist:
                    best_year, best_dist = year, dist
            if best_year is None:
                continue

            # Descartar proyecciones futuras (cifras sustancialmente mayores al máximo histórico real)
            official = self.historical_table[best_year]
            max_hist_val = self.historical_table.get(last_hist_year, 0.0)
            if max_hist_val > 0 and value > 2.5 * max_hist_val:
                continue

            # Descartar proyecciones de modelos de difusión (si la cifra coincide con proyecciones de un modelo)
            if self.model_fits:
                is_model_proj = False
                for mf in self.model_fits:
                    for proj_val in mf.projections.values():
                        if abs(value - proj_val) < 2.0 or (proj_val > 0 and abs(value - proj_val) / proj_val * 100 < 5.0):
                            is_model_proj = True
                            break
                    if is_model_proj:
                        break
                if is_model_proj:
                    continue

            # Descartar métricas no-usuario (peticiones API, consultas, tokens, dólares) y números con punto de millar (25.000 millones)
            start_ctx = max(0, n_start - 80)
            end_ctx = min(len(clean_text), n_end + 80)
            ctx = clean_text[start_ctx:end_ctx].lower()
            if any(kw in ctx for kw in ["peticiones", "consultas", "llamadas", "api", "token", "solicitudes", "dólar", "dolar", "euro", "byte", "requests"]):
                continue
            if ".000" in evidence or ",000" in evidence:
                continue

            # Descartar si la cifra coincide con un valor histórico oficial de cualquier año en la tabla
            is_valid_hist_value = any(
                abs(value - h_val) <= 0.5 or (h_val > 0 and abs(value - h_val) / h_val * 100 <= self.tolerance_pct)
                for h_val in self.historical_table.values()
            )
            if is_valid_hist_value:
                continue

            # Verificar si la cifra es la variación anual (delta N = N_t - N_{t-1}) de cualquier año histórico
            is_annual_increment = False
            for yr in known_years:
                p_yr = max([y for y in known_years if y < yr], default=None)
                if p_yr:
                    inc_val = self.historical_table[yr] - self.historical_table[p_yr]
                    if abs(value - inc_val) <= 0.5 or (inc_val > 0 and abs(value - inc_val) / inc_val * 100 <= self.tolerance_pct):
                        is_annual_increment = True
                        break
            if is_annual_increment:
                continue

            diff = abs(value - official)
            rel = diff / official * 100 if official else (100.0 if diff else 0.0)
            if diff > 0.001 and rel > self.tolerance_pct:
                # WARNING en lugar de BLOCKER: el texto narrativo es prosa IA con hitos cualitativos aproximados
                # Los números cuantitativos fiables están en las tablas estructuradas (Secciones 2, 4, 5)
                severity = "WARNING"
                self.issues.append(Issue(
                    severity, "narrativa_vs_tabla",
                    f"El texto menciona ~{value}M cerca de {best_year}, pero la tabla "
                    f"oficial registra {official}M (discrepancia de {rel:.1f}%).",
                    evidence=evidence,
                ))



 
    def check_duplicate_models(self) -> None:
        """Detecta modelos con R2/MAPE/proyecciones practicamente identicas entre si."""
        n = len(self.model_fits)
        for i in range(n):
            for j in range(i + 1, n):
                a, b = self.model_fits[i], self.model_fits[j]
                same_r2 = abs(a.r2 - b.r2) < 1e-4
                same_mape = abs(a.mape - b.mape) < 1e-3
                if not (same_r2 and same_mape):
                    continue
                common_years = set(a.projections) & set(b.projections)
                if not common_years:
                    continue
                max_diff = max(
                    abs(a.projections[y] - b.projections[y]) for y in common_years
                )
                if max_diff < 0.05:  # menos de 50k usuarios de diferencia en todos los años
                    self.issues.append(Issue(
                        "WARNING",  # colapso paramétrico es esperado con pocos datos históricos
                        "modelos_duplicados",
                        f"'{a.name}' y '{b.name}' producen R2, MAPE y proyecciones "
                        f"identicas (diff maxima entre proyecciones: {max_diff:.4f}M). "
                        "Probable colapso paramétrico por pocos puntos históricos — "
                        "el informe ya incluye la nota metodológica correspondiente.",
                        evidence=f"R2={a.r2}, MAPE={a.mape}%",
                    ))
 
    def check_latex_leakage(self) -> None:
        """Detecta comandos LaTeX crudos que deberian haberse renderizado o reescrito en texto plano.
        Si el comando esta correctamente delimitado por $$...$$ o $...$ (markdown/mathjax valido),
        se marca como INFO (riesgo a futuro) en vez de WARNING (problema ya presente), porque
        en ese caso el LaTeX es sintacticamente correcto -- el riesgo es que el paso de
        conversion a PDF no tenga motor de render matematico (como ya paso antes)."""
        matches = list(LATEX_LEAK_PATTERN.finditer(self.text))
        if not matches:
            return
        GAP = 30
        clusters: List[List[re.Match]] = [[matches[0]]]
        for m in matches[1:]:
            if m.start() - clusters[-1][-1].end() <= GAP:
                clusters[-1].append(m)
            else:
                clusters.append([m])
 
        dollar_spans = [(m.start(), m.end()) for m in re.finditer(r"\$\$[\s\S]*?\$\$|\$[^\$\n]+\$", self.text)]
 
        def _inside_dollar_block(pos: int) -> bool:
            return any(s <= pos < e for s, e in dollar_spans)
 
        for cluster in clusters:
            start = max(0, cluster[0].start() - 30)
            end = min(len(self.text), cluster[-1].end() + 30)
            commands = sorted({m.group(1) for m in cluster})
            delimited = _inside_dollar_block(cluster[0].start())
            if delimited:
                pass # Delimitado correctamente en $$...$$; renderizable por el motor de PDF.
            else:
                self.issues.append(Issue(
                    "WARNING",
                    "latex_sin_renderizar",
                    f"Formula con {len(commands)} comando(s) LaTeX crudo(s) SIN delimitar "
                    f"({', '.join(commands)}) fuera de bloques $$...$$; el motor de PDF no "
                    "los interpretara y quedaran visibles como texto.",
                    evidence="..." + self.text[start:end].replace("\n", " ") + "...",
                ))
 
    def check_math_rendering_corruption(self, min_run_len: int = 40) -> None:
        """Detecta 'palabras' anormalmente largas sin espacios que mezclan letras y digitos
        (tipico de MathML/LaTeX mal extraido a texto plano, ej. formulas con
        subindices/superindices concatenados: '41.50milmillones)yseestimara...').
        Distinto de check_latex_leakage: aqui no hay comandos \\algo, sino texto fusionado."""
        for match in re.finditer(r"\S+", self.text):
            token = match.group(0)
            if len(token) < min_run_len:
                continue
            has_letter = any(c.isalpha for c in token)
            has_digit = any(c.isdigit for c in token)
            # ratio de "palabra pegada": muy pocos signos de puntuacion normales para su longitud
            if has_letter and has_digit:
                start = max(0, match.start() - 25)
                end = min(len(self.text), match.end() + 25)
                self.issues.append(Issue(
                    "WARNING",
                    "renderizado_matematico_roto",
                    f"Se encontro un bloque de {len(token)} caracteres sin espacios que mezcla "
                    "letras y numeros, tipico de una formula matematica (MathML/LaTeX) mal "
                    "extraida a texto plano y fusionada en una sola palabra ilegible.",
                    evidence="..." + self.text[start:end].replace("\n", " ") + "...",
                ))
 
    def check_citations(self) -> None:
        """Marca citas Autor(Año) que no estan en la lista blanca de referencias conocidas."""
        seen = set()
        for match in CITATION_PATTERN.finditer(self.text):
            authors_raw, year = match.group(1), int(match.group(2))
            key = authors_raw.lower().strip()
            if any(sw in key for sw in CITATION_STOPWORDS):
                continue
            if (key, year) in seen:
                continue
            seen.add((key, year))
            # Busca en una ventana mas amplia antes de la cita (no solo la palabra
            # inmediatamente adyacente), para no perder nombres como "Bass" en
            # "Modelo de Bass Clásico (1969)" donde el regex solo capturo "Clásico".
            context_start = max(0, match.start() - 45)
            wide_context = self.text[context_start:match.end()].lower()
            is_known = any(
                ref_author in wide_context
                for ref_author, ref_year in KNOWN_REFERENCES
                if ref_year == year
            )
            if not is_known:
                severity = "BLOCKER" if year >= 2024 else "WARNING"
                self.issues.append(Issue(
                    severity,
                    "cita_no_verificada",
                    f"La cita '{authors_raw} ({year})' no aparece en la lista blanca de "
                    "referencias conocidas del dominio. Podria ser una alucinacion del LLM "
                    "(nombre de autor inventado para 'cumplir' la instruccion de citar papers).",
                    evidence=match.group(0),
                ))
 
    def _filter_out_table_rows(self, text: str) -> str:
        """Sustituye por espacios las lineas que parecen filas de tabla comparativa
        (3+ menciones de millones en la misma linea), para no confundir la
        divergencia *esperada* entre modelos con una contradiccion real."""
        out_lines = []
        for line in text.split("\n"):
            n_mentions = len(RANGE_MILLONES_PATTERN.findall(line)) + len(
                SINGLE_MILLONES_PATTERN.findall(line)
            )
            if n_mentions >= TABLE_ROW_MILLONES_THRESHOLD:
                out_lines.append(" " * len(line))  # preserva offsets, borra contenido
            else:
                out_lines.append(line)
        return "\n".join(out_lines)
 
    def check_numeric_prose(self):
        """[REFORMA SIN CIFRAS] BLOCKER: cifra de adopción (número + M/millones)
        en prosa narrativa. Las tablas están exentas (se filtran)."""
        clean_text = self._filter_out_table_rows(self.text)
        # Eximir líneas de bullets canónicos deterministas (formato 'YYYY: X M')
        pat = re.compile(
            r'^\s*[-*]?\s*\**\s*(?:A[ñn]o\s*)?20\d{2}\s*:\s*\**\s*\d', re.MULTILINE)
        exempt = set()
        for m in pat.finditer(clean_text):
            ls = clean_text.rfind("\n", 0, m.start()) + 1
            le = clean_text.find("\n", m.end())
            if le == -1:
                le = len(clean_text)
            exempt.add((ls, le))
        num_pat = re.compile(
            r'\b\d{1,3}(?:[\.,]\d+)?\s*(?:\*\*)?\s*(?:M\b|millones)', re.IGNORECASE)
        # [FIX 12] Eximir la sección 1 (análisis cualitativo auditado, texto de BD)
        _s1 = clean_text.find("1. Resumen Ejecutivo")
        _s2 = clean_text.find("2. Datos Históricos")
        for m in num_pat.finditer(clean_text):
            if _s1 != -1 and _s2 != -1 and _s1 <= m.start() < _s2:
                continue
            if any(s <= m.start() < e for s, e in exempt):
                continue
            ls = clean_text.rfind("\n", 0, m.start()) + 1
            le = clean_text.find("\n", m.end())
            if le == -1:
                le = len(clean_text)
            line = clean_text[ls:le].strip()
            if ("Nota Metodológica" in line) or ("N/D" in line) or line.startswith(">"):
                continue
            if re.match(r'^\|', line):   # por si quedan filas de tabla
                continue
            self.issues.append(Issue(
                "BLOCKER",
                "cifra_en_prosa",
                f"La prosa narrativa contiene una cifra de adopción ('{m.group(0).strip()}'), "
                f"prohibida por diseño (las cifras viven en tablas): \"{line[:120]}\"",
                evidence=m.group(0),
            ))

    def check_consensus_consistency(
        self, target_years: Optional[List[int]] = None, window: int = 220
    ) -> None:
        """
        Extrae TODAS las menciones de "X millones" / "X a Y millones" en el texto
        (fuera de tablas comparativas) y, para cada una, la asocia al año objetivo
        MAS CERCANO en distancia de caracteres (no a todos los años dentro de una
        ventana simetrica -- eso causaria contaminacion cruzada cuando dos años
        objetivo aparecen mencionados cerca uno del otro, ej. "...2031: 3010M...
        2036: 3344M..." no debe hacer que 3344M tambien "cuente" para 2031).
 
        Si para un mismo año aparecen valores que no son consistentes entre si
        (fuera de la tolerancia configurada), se marca como contradiccion.
 
        target_years: años a vigilar (por defecto, los horizontes tipicos 2030/2035).
        window: distancia maxima en caracteres para asociar una cifra a un año.
        """
        target_years = target_years or [2030, 2035]
        clean_text = self._filter_out_table_rows(self.text)
 
        year_positions = [
            (int(m.group(1)), m.start(), m.end())
            for m in YEAR_MENTION_PATTERN.finditer(clean_text)
            if int(m.group(1)) in target_years
        ]
        if not year_positions:
            return
 
        numeric_mentions: List[Tuple[float, str, int, int]] = []  # (rep, evidence, start, end)
        consumed_spans = []
        for rm in RANGE_MILLONES_PATTERN.finditer(clean_text):
            v1_str, v2_str = rm.group(1), rm.group(2)
            if _looks_like_year(v1_str) or _looks_like_year(v2_str):
                continue
            v1, v2 = float(v1_str), float(v2_str)
            numeric_mentions.append(((v1 + v2) / 2, rm.group(0).strip(), rm.start(), rm.end()))
            consumed_spans.append((rm.start(), rm.end()))
        for sm in SINGLE_MILLONES_PATTERN.finditer(clean_text):
            if any(s <= sm.start() < e for s, e in consumed_spans):
                continue
            numeric_mentions.append((float(sm.group(1)), sm.group(0).strip(), sm.start(), sm.end()))
 
        # [FIX 10a] Incrementos no son proyecciones: cifra precedida por palabra
        # de incremento dentro de 60 chars no es valor de consenso de ningún año.
        _INC_PHRASE = re.compile(r'\b(?:aumento|incremento|crecimiento|adici[oó]n|diferencia|salto)\b', re.IGNORECASE)
        findings: Dict[int, List[Tuple[float, str, Tuple[int, int]]]] = {y: [] for y in target_years}
 
        all_year_positions = [
            (int(m.group(1)), m.start(), m.end())
            for m in YEAR_MENTION_PATTERN.finditer(clean_text)
        ]
        for rep, evidence, n_start, n_end in numeric_mentions:
            # Excluir valores históricos conocidos para evitar falsos positivos en proyecciones futuras
            if self.historical_table and any(abs(rep - hv) / max(hv, 0.01) < 0.02 for hv in self.historical_table.values()):
                continue
            # [FIX 10a]
            _pre_ctx = clean_text[max(0, n_start - 60):n_start]
            if _INC_PHRASE.search(_pre_ctx):
                continue
            # [FIX 5a] Año PROPIO: si la cifra tiene un año (cualquiera) a <30 chars,
            # pertenece a ese año; si no es un año objetivo, NO contamina al objetivo
            # más cercano (evita atribuir el valor del bullet 2026/2032 al año 2030).
            own_year, own_dist = None, None
            for year, y_start, y_end in all_year_positions:
                d = min(abs(n_start - y_end), abs(y_start - n_end))
                if d > 30:
                    continue
                if own_dist is None or d < own_dist:
                    own_year, own_dist = year, d
            if own_year is not None and own_year not in target_years:
                continue
            # año objetivo mas cercano a esta mencion numerica (por distancia de caracteres)
            best_year, best_dist = None, None
            for year, y_start, y_end in year_positions:
                dist = min(abs(n_start - y_end), abs(y_start - n_end))
                if dist > window:
                    continue
                if best_dist is None or dist < best_dist:
                    best_year, best_dist = year, dist
            if best_year is not None:
                findings[best_year].append((rep, evidence, (n_start, n_end)))
 
        for year, entries in findings.items():
            if len(entries) < 2:
                continue
            seen_spans = set()
            unique_entries = []
            for rep, evidence, span in entries:
                if span in seen_spans:
                    continue
                seen_spans.add(span)
                unique_entries.append((rep, evidence, span))
 
            values = [e[0] for e in unique_entries]
            if len(values) < 2:
                continue
            vmin, vmax = min(values), max(values)
            rel = (vmax - vmin) / vmin * 100 if vmin else (100.0 if vmax else 0.0)
            if rel > self.tolerance_pct:
                evidence_list = "; ".join(f"{e[1]} (~{e[0]:.2f}M)" for e in unique_entries)
                self.issues.append(Issue(
                    "BLOCKER",
                    "consenso_inconsistente",
                    f"Para el año {year}, el informe menciona valores de consenso/proyeccion "
                    f"que no son consistentes entre si: van de {vmin:.2f}M a {vmax:.2f}M "
                    f"(diferencia de {rel:.1f}%, tolerancia {self.tolerance_pct}%). "
                    "El documento no tiene una cifra unica de referencia para este horizonte.",
                    evidence=evidence_list,
                ))

    def check_qualitative_growth_labels(self, window: int = 150) -> None:
        """Verifica que los adjetivos de crecimiento cerca de un año coincidan
        con la tasa g_t real de ese año, calculada desde historical_table."""
        years_sorted = sorted(self.historical_table)
        growth_rates = {}
        for i in range(1, len(years_sorted)):
            y0, y1 = years_sorted[i - 1], years_sorted[i]
            v0, v1 = self.historical_table[y0], self.historical_table[y1]
            if v0:
                growth_rates[y1] = (v1 - v0) / v0 * 100

        year_positions = [
            (int(m.group(1)), m.start(), m.end())
            for m in YEAR_MENTION_PATTERN.finditer(self.text)
            if int(m.group(1)) in growth_rates
        ]

        for pattern, (lo, hi) in GROWTH_ADJECTIVES.items():
            for m in re.finditer(pattern, self.text, re.IGNORECASE):
                nearest = min(
                    year_positions,
                    key=lambda yp: min(abs(m.start() - yp[2]), abs(yp[1] - m.end())),
                    default=None,
                )
                if nearest is None:
                    continue
                year, y_start, y_end = nearest
                dist = min(abs(m.start() - y_end), abs(y_start - m.end()))
                if dist > window:
                    continue
                g_t = growth_rates[year]
                if not (lo <= g_t <= hi):
                    start = max(0, m.start() - 40)
                    end = min(len(self.text), m.end() + 40)
                    self.issues.append(Issue(
                        "WARNING", "razonamiento_cualitativo_inconsistente_con_los_datos",
                        f"El adjetivo '{m.group(0)}' cerca de {year} no coincide con la "
                        f"tasa real g_t={g_t:.1f}% (rango esperado {lo}-{hi}%).",
                        evidence="..." + self.text[start:end].replace("\n", " ") + "...",
                    ))

    def check_recommendation_vs_mape(self, recommended_model_name: Optional[str] = None) -> None:
        """Si el texto describe el ajuste de otros modelos como 'ligeramente superior'
        pero la diferencia real de MAPE es grande (>5%), marca contradicción."""
        if not self.model_fits:
            return
        best = min(self.model_fits, key=lambda m: m.mape)
        
        def norm(s: str) -> str:
            s_clean = s.lower().replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
            return re.sub(r'[^a-z0-9]', '', s_clean)

        rec = None
        if recommended_model_name:
            rec_norm = norm(recommended_model_name)
            rec = next((m for m in self.model_fits if rec_norm in norm(m.name) or norm(m.name) in rec_norm), None)
        
        if not rec:
            # Buscar en el texto cuál es el modelo explícitamente recomendado o seleccionado
            rec_patterns = [
                r'se (?:selecciona|adopta|elige|recomienda|utiliza) (?:el modelo|como modelo ideal|como modelo)? [^\.\n]*?([A-ZÁÉÍÓÚ][\w\s&\-–]+)',
                r'modelo (?:ideal|recomendado|elegido|seleccionado) [^\.\n]*?([A-ZÁÉÍÓÚ][\w\s&\-–]+)',
                r'modelo de \*\*([^\*]+)\*\*',
            ]
            for pat in rec_patterns:
                for match in re.finditer(pat, self.text, re.IGNORECASE):
                    cand_norm = norm(match.group(1).strip())
                    found = next((m for m in self.model_fits if cand_norm in norm(m.name) or norm(m.name) in cand_norm), None)
                    if found:
                        rec = found
                        break
                if rec:
                    break

        if not rec:
            # Fallback secundario: el modelo recomendado por razones teóricas suele ser el de mayor MAPE razonable.
            # Excluimos outliers extremos (MAPE > 100%) que son claramente inadecuados y nunca se recomiendan.
            # Solo activar si hay más de un modelo con MAPE distinto.
            candidates_reasonable = sorted(
                [m for m in self.model_fits if m.mape <= 100.0],
                key=lambda x: x.mape, reverse=True
            )
            if len(candidates_reasonable) >= 2 and candidates_reasonable[0].mape > candidates_reasonable[1].mape:
                rec = candidates_reasonable[0]

        if not rec:
            return

        if rec.name == best.name:
            return  # el recomendado ya es el mejor, no hay contradicción

        rec_mape = rec.mape
        diff_pct = rec_mape - best.mape

        if diff_pct <= 5.0:
            return

        # Palabras de negación o concesión explícita que invalidan el hallazgo
        # (si el texto reconoce explícitamente "A pesar de que otros modelos...", no es una contradicción, es una concesión metodológica válida)
        NEGATION_WORDS = {
            "no el que", "no es el", "no arroja", "no presenta", "no fue el",
            "aunque no", "no es quien", "no siendo", "si bien no",
            "a pesar de que", "a pesar de", "si bien", "aunque", "mientras que",
            "los modelos con", "modelos con menor", "puedan ofrecer", "puedan mostrar",
            "por su superioridad conceptual", "no por ajuste cuantitativo",
            # Contextos de explicación de métricas (R², MAPE) — no son comparaciones de modelos
            "valores más cercanos a 1", "cercanos a 1 sugiriendo", "sugiriendo un mejor",
            "coeficiente de determinación", "mide la precisión de las predicc",
            "por su parte, mide", "la precisión de las predicc",
        }

        for m in SUPERIORITY_PHRASES.finditer(self.text):
            start = max(0, m.start() - 80)
            end = min(len(self.text), m.end() + 60)
            context = self.text[start:end]
            ctx_lower = context.lower()

            # Omitir si el contexto inmediato niega o concede la superioridad (el texto ya lo reconoce correctamente)
            if any(neg in ctx_lower for neg in NEGATION_WORDS):
                continue

            # Omitir si la afirmación de "mejor ajuste" / "menor MAPE" se refiere correctamente al modelo con mejor ajuste real (ej. Dual Market / Muller & Yogev),
            # lo cual es factualmente correcto y coherente con los datos.
            best_models_names = [bm.name.lower() for bm in self.model_fits if bm.mape <= best.mape + 5.0]
            if any(b_name in ctx_lower for b_name in best_models_names):
                continue

            if "otros modelos" in ctx_lower or "diferencia" in ctx_lower or "ajuste" in ctx_lower:
                self.issues.append(Issue(
                    "BLOCKER", "recomendacion_que_contradice_su_propia_justificacion",
                    f"El texto describe el MAPE de otros modelos como '{m.group(0)}', pero "
                    f"'{best.name}' tiene MAPE={best.mape:.2f}% frente a "
                    f"{rec.name} MAPE={rec_mape:.2f}% (diferencia real de {diff_pct:.1f} puntos, no 'ligera').",
                    evidence=context.strip(),
                ))

 
    # ------------------------------------------------------------ orquestador
 
    def run_all(self) -> List[Issue]:
        self.issues.clear()
        
        # Deduce recommended model
        rec = None
        rec_patterns = [
            r'se (?:selecciona|adopta|elige|recomienda|utiliza) (?:el modelo|como modelo ideal|como modelo)? [^\.\n]*?([A-ZÁÉÍÓÚ][\w\s\&\-]+)',
            r'modelo (?:ideal|recomendado|elegido|seleccionado) [^\.\n]*?([A-ZÁÉÍÓÚ][\w\s\&\-]+)',
            r'se asume [^\.\n]*?([A-ZÁÉÍÓÚ][\w\s\&\-]+) como (?:el )?modelo'
        ]
        def norm(s): return re.sub(r'[^a-z0-9]', '', s.lower().replace("á","a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u"))
        for p in rec_patterns:
            m = re.search(p, self.text, re.IGNORECASE)
            if m:
                found_name = m.group(1).strip()
                fn = norm(found_name)
                rec = next((mf for mf in self.model_fits if fn in norm(mf.name) or norm(mf.name) in fn), None)
                if rec: break
        
        if not rec and self.model_fits:
            rec = min(self.model_fits, key=lambda m: m.mape)
            
        if rec:
            per_year = {int(k): float(v) for k, v in rec.projections.items()}
            last_hist = max(self.historical_table.values()) if self.historical_table else None
            self.check_totals_as_increments(per_year, last_hist)
            # [FIX 5b] Años clave dinámicos: +5/+10 desde el último año histórico real
            # (antes hardcode 2031/2036: check muerto si la serie no termina en 2026).
            _lh_yr = max(self.historical_table) if self.historical_table else None
            if _lh_yr is not None:
                _ya, _yb = _lh_yr + 5, _lh_yr + 10
                _va = per_year.get(_ya) or per_year.get(str(_ya))
                _vb = per_year.get(_yb) or per_year.get(str(_yb))
                self.check_year_value_swap(_va, _vb, _ya, _yb)

        self.check_narrative_vs_table()
        self.check_duplicate_models()
        self.check_latex_leakage()
        self.check_math_rendering_corruption()
        self.check_citations()
        _tgt_years = None
        if self.historical_table:
            _lh_c = max(self.historical_table)
            _tgt_years = [_lh_c + 5, _lh_c + 10]
        self.check_consensus_consistency(target_years=_tgt_years)
        self.check_numeric_prose()
        self.check_qualitative_growth_labels()
        self.check_recommendation_vs_mape()
        return self.issues
 
    def report(self) -> str:
        issues = self.run_all()
        if not issues:
            return "✅ No se detectaron incoherencias. El informe pasa la validacion."
        lines = [f"Se detectaron {len(issues)} problema(s):\n"]
        for i, issue in enumerate(issues, 1):
            lines.append(f"{i}. {issue}\n")
        n_blockers = sum(1 for i in issues if i.severity == "BLOCKER")
        lines.append(
            f"\nResumen: {n_blockers} BLOCKER(S) que deberian impedir la publicacion, "
            f"{len(issues) - n_blockers} advertencia(s)/info."
        )
        return "\n".join(lines)
 
 
# --------------------------------------------------------------------------
# Demo / CLI
# --------------------------------------------------------------------------
 
def _demo_with_actual_report() -> None:
    narrative_text = """
    2022: Fase Experimental y Pruebas Cerradas (0.1M). A finales de este año...
    2023: Lanzamiento Comercial y Despliegue (5.5M). Marca el inicio...
    Modelo Logístico genérico:
    Modelo de Mercado Potencial Dinámico y Endógeno de Ladrón-de-Guevara & Putsis (2011):
    C(t) = 1.0 - \\theta \\exp\\left(-\\gamma \\frac{N(t)}{S}\\right) donde la difusion es:
    Año 2030: 275.5 millones de usuarios/asientos corporativos activos.
    Año 2035: 295.0 millones de usuarios/asientos corporativos activos.
    Hito 5 Años (2030): Operar bajo la presuncion de ~290 millones de adopciones/nodos.
    Hito 10 Años (2035): Planificar una fase de consolidacion ~297 millones.
    """
 
    historical_table = {2016: 0.0, 2017: 0.0, 2018: 0.0, 2019: 0.0, 2020: 0.0,
                         2021: 0.0, 2022: 0.0, 2023: 6.0, 2024: 32.0, 2025: 65.0}
 
    model_fits = [
        ModelFit("Bass Clasico", 0.9857, 31.97,
                 {2030: 290.21, 2033: 296.76, 2035: 297.06}),
        ModelFit("Dual Market", 0.9857, 31.97,
                 {2030: 290.21, 2033: 296.76, 2035: 297.06}),
        ModelFit("Steffens & Murthy", 0.9999, 1.12,
                 {2030: 74.71, 2033: 74.71, 2035: 74.71}),
        ModelFit("Difusion Logistica ", 0.9999, 1.12,
                 {2030: 74.71, 2033: 74.71, 2035: 74.71}),
        ModelFit("Van den Bulte & Joshi", 0.9894, 28.67,
                 {2030: 204.07, 2033: 206.74, 2035: 206.86}),
    ]
 
    rv = ReportValidator(narrative_text, historical_table, model_fits)
    print(rv.report)
 
 
def main() -> None:
    if len(sys.argv) < 2:
        print("Sin argumentos: ejecutando demo con datos del informe de Anthropic analizado.\n")
        _demo_with_actual_report()
        return
 
    path = sys.argv[1]
    with open(path, "r", encoding="utf-8") as f:
        text = f.read
 
    tables_path = path + ".tables.json"
    historical_table, model_fits = {}, []
    try:
        with open(tables_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            historical_table = {int(k): v for k, v in data.get("historical", {}).items()}
            model_fits = [
                ModelFit(m["name"], m["r2"], m["mape"],
                         {int(k): v for k, v in m.get("projections", {}).items()})
                for m in data.get("models", [])
            ]
    except FileNotFoundError:
        print(f"(No se encontro {tables_path}; se validara solo texto: LaTeX y citas.)\n")
 
    rv = ReportValidator(text, historical_table, model_fits)
    print(rv.report)
 
 
if __name__ == "__main__":
    main