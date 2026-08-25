import sys
import os
sys.path.append(os.path.abspath("C:/Users/roset/Bass"))
from report_validator import ReportValidator
from data.report_compiler import strip_numeric_prose
import re

new_block = r"""
### 📐 Formulación Matemática de los Modelos Evaluados

* **Bass Clásico (1969)** — Modelo de Bass Clásico:
  x(t) = m * (1 - exp(-(p + q) * t)) / (1 + (q / p) * exp(-(p + q) * t))
  
* **Dual Market (Roset & Canals, 2011)** — Modelo de Dos Mercados Independientes:
  x(t) = x1(t) + x2(t), donde x1 y x2 son modelos clásicos de Bass independientes:
  xi(t) = mi * (1 - exp(-(pi + qi) * t)) / (1 + (qi / pi) * exp(-(pi + qi) * t))
  
* **Fourt & Woodlock (1960)** — Modelo de Innovación Pura:
  N(t) = m * (1 - exp(-p * t))
  
* **Gompertz (1825)** — Modelo Asimétrico de Gompertz:
  N(t) = m * exp(-exp(-k * (t - t0)))
  
* **Bass Generalizado (GBM) (1994)** — Modelo de Bass Generalizado:
  dN/dt = (p + (q / m) * N(t)) * (m - N(t)) * (1 + beta * t)
  
* **Horsky & Simon (1983)** — Modelo con Publicidad:
  dN/dt = (p0 + alpha * ln(1 + t) + (q / m) * N(t)) * (m - N(t))
  
* **Muller & Yogev (2006)** — Modelo del Efecto Saddle:
  I(t) = Ni * (1 - exp(-(pi + qi) * t)) / (1 + (qi / pi) * exp(-(pi + qi) * t))
  dM/dt = (pm + qm * M(t) / (Ni + Nm) + qim * I(t) / (Ni + Nm)) * (Nm - M(t))
  
* **Van den Bulte & Joshi (2007)** — Modelo de Influenciadores e Imitadores:
  F1(t) = (1 - exp(-(p1 + q1) * t)) / (1 + (q1 / p1) * exp(-(p1 + q1) * t))
  dF2/dt = q2 * (w * F1(t) + (1 - w) * F2(t)) * (1 - F2(t))
  N(t) = M1 * F1(t) + M2 * F2(t)
  
* **Difusión Logística R&K (Ryu & Kim, 2025)** — Modelo Logístico de Difusión-Convergencia:
  L(t) = b1 / (1 + ((b1 - b0) / b0) * exp(-k2 * (t - t0)))
  
* **Ladrón-de-Guevara & Putsis (2011)** — Modelo de Mercado Potencial Dinámico y Endógeno:
  C(t) = 1.0 - theta * exp(-gamma * N(t) / S), donde M(t) = C(t) * S y la difusión es:
  dN/dt = (alpha + beta * (N / M)) * (M - N)
"""

print("1. Pattern evaluation for bullets-AÑO exemption:")
pattern_strip = re.compile(r'^\s*[-*]?\s*\**\s*(?:A[ñn]o\s*)?20\d{2}\s*:')
pattern_check = re.compile(r'^\s*[-*]?\s*\**\s*(?:A[ñn]o\s*)?20\d{2}\s*:\s*\**\s*\d', re.MULTILINE)
print("Hits in strip_numeric_prose pattern:", len(pattern_strip.findall(new_block)))
print("Hits in check_numeric_prose pattern:", len(pattern_check.findall(new_block)))

print("\n2. Executing functions against block (embedded in natural context, Section 2)")
text_context = "## 🤖 2. Datos Históricos y Resumen de Ajuste de Modelos\n" + new_block + "\n## 🤖 3. Tabla de Desviación Histórica Año a Año"

stripped = strip_numeric_prose(text_context)
if stripped == text_context:
    print("strip_numeric_prose -> 0 hits (block left intact)")
else:
    print("strip_numeric_prose -> MODIFIED block")

val = ReportValidator(text_context, [])
val.check_numeric_prose()
if not val.issues:
    print("check_numeric_prose -> 0 hits (no issues found)")
else:
    for issue in val.issues:
        print(f"check_numeric_prose -> {issue.category} - {issue.evidence}")
