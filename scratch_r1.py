import re
from difflib import ndiff
import sys
import os

# Set up paths to import Bass modules
sys.path.append(os.path.abspath("C:/Users/roset/Bass"))

from data.report_compiler import strip_numeric_prose
from report_validator import ReportValidator

# Original block
original_block = r"""
### 📐 Formulación Matemática de los Modelos Evaluados

* **Modelo de Bass Clásico (1969)**:
  x(t) = m * (1 - exp(-(p + q) * t)) / (1 + (q / p) * exp(-(p + q) * t))
  
* **Modelo de Dos Mercados Independientes - Roset & Canals (2011)**:
  x(t) = x1(t) + x2(t), donde x1 y x2 son modelos clásicos de Bass independientes:
  xi(t) = mi * (1 - exp(-(pi + qi) * t)) / (1 + (qi / pi) * exp(-(pi + qi) * t))
  
* **Modelo de Innovación Pura de Fourt & Woodlock (1960)**:
  N(t) = m * (1 - exp(-p * t))
  
* **Modelo Asimétrico de Gompertz**:
  N(t) = m * exp(-exp(-k * (t - t0)))
  
* **Modelo de Bass Generalizado - GBM (1994)**:
  dN/dt = (p + (q / m) * N(t)) * (m - N(t)) * (1 + beta * t)
  
* **Modelo con Publicidad de Horsky & Simon (1983)**:
  dN/dt = (p0 + alpha * ln(1 + t) + (q / m) * N(t)) * (m - N(t))
  
* **Modelo del Efecto Saddle de Muller & Yogev (2006)**:
  I(t) = Ni * (1 - exp(-(pi + qi) * t)) / (1 + (qi / pi) * exp(-(pi + qi) * t))
  dM/dt = (pm + qm * M(t) / (Ni + Nm) + qim * I(t) / (Ni + Nm)) * (Nm - M(t))
  
* **Modelo de Influenciadores e Imitadores de Van den Bulte & Joshi (2007)**:
  F1(t) = (1 - exp(-(p1 + q1) * t)) / (1 + (q1 / p1) * exp(-(p1 + q1) * t))
  dF2/dt = q2 * (w * F1(t) + (1 - w) * F2(t)) * (1 - F2(t))
  N(t) = M1 * F1(t) + M2 * F2(t)
  
* **Modelo Logístico de Difusión-Convergencia (Ryu & Kim, 2025)**:
  L(t) = b1 / (1 + ((b1 - b0) / b0) * exp(-k2 * (t - t0)))
  
* **Modelo de Mercado Potencial Dinámico y Endógeno de Ladrón-de-Guevara & Putsis (2011)**:
  C(t) = 1.0 - theta * exp(-gamma * N(t) / S), donde M(t) = C(t) * S y la difusión es:
  dN/dt = (alpha + beta * (N / M)) * (M - N)
"""

MODEL_LABELS = {
    "Bass_Clasico": "Bass Clásico",
    "Dual_Market": "Dual Market",
    "Fourt_Woodlock": "Fourt & Woodlock",
    "Gompertz": "Gompertz",
    "Generalized_Bass": "Bass Generalizado (GBM)",
    "Horsky_Simon": "Horsky & Simon",
    "Muller_Yogev": "Muller & Yogev",
    "VdB_Joshi": "Van den Bulte & Joshi",
    "Logistic_Diffusion_Convergence": "Difusión Logística R&K",
    "Ladron_Putsis": "Ladrón-de-Guevara & Putsis",
}

MODEL_YEARS = {
    "Bass Clásico": 1969,
    "Dual Market": 2011,
    "Fourt & Woodlock": 1960,
    "Gompertz": 1825,
    "Bass Generalizado (GBM)": 1994,
    "Horsky & Simon": 1983,
    "Muller & Yogev": 2006,
    "Van den Bulte & Joshi": 2007,
    "Ladrón-de-Guevara & Putsis": 2011,
    "Difusión Logística R&K": 2025, # Fixed key for Ryu & Kim to match model_labels
}

MODEL_EQUATIONS = {
    "Bass_Clasico": {
        "desc": "Modelo de Bass Clásico", "autores": "",
        "eq": "  x(t) = m * (1 - exp(-(p + q) * t)) / (1 + (q / p) * exp(-(p + q) * t))"
    },
    "Dual_Market": {
        "desc": "Modelo de Dos Mercados Independientes", "autores": "Roset & Canals",
        "eq": "  x(t) = x1(t) + x2(t), donde x1 y x2 son modelos clásicos de Bass independientes:\n  xi(t) = mi * (1 - exp(-(pi + qi) * t)) / (1 + (qi / pi) * exp(-(pi + qi) * t))"
    },
    "Fourt_Woodlock": {
        "desc": "Modelo de Innovación Pura", "autores": "",
        "eq": "  N(t) = m * (1 - exp(-p * t))"
    },
    "Gompertz": {
        "desc": "Modelo Asimétrico de Gompertz", "autores": "",
        "eq": "  N(t) = m * exp(-exp(-k * (t - t0)))"
    },
    "Generalized_Bass": {
        "desc": "Modelo de Bass Generalizado", "autores": "",
        "eq": "  dN/dt = (p + (q / m) * N(t)) * (m - N(t)) * (1 + beta * t)"
    },
    "Horsky_Simon": {
        "desc": "Modelo con Publicidad", "autores": "",
        "eq": "  dN/dt = (p0 + alpha * ln(1 + t) + (q / m) * N(t)) * (m - N(t))"
    },
    "Muller_Yogev": {
        "desc": "Modelo del Efecto Saddle", "autores": "",
        "eq": "  I(t) = Ni * (1 - exp(-(pi + qi) * t)) / (1 + (qi / pi) * exp(-(pi + qi) * t))\n  dM/dt = (pm + qm * M(t) / (Ni + Nm) + qim * I(t) / (Ni + Nm)) * (Nm - M(t))"
    },
    "VdB_Joshi": {
        "desc": "Modelo de Influenciadores e Imitadores", "autores": "",
        "eq": "  F1(t) = (1 - exp(-(p1 + q1) * t)) / (1 + (q1 / p1) * exp(-(p1 + q1) * t))\n  dF2/dt = q2 * (w * F1(t) + (1 - w) * F2(t)) * (1 - F2(t))\n  N(t) = M1 * F1(t) + M2 * F2(t)"
    },
    "Logistic_Diffusion_Convergence": {
        "desc": "Modelo Logístico de Difusión-Convergencia", "autores": "Ryu & Kim",
        "eq": "  L(t) = b1 / (1 + ((b1 - b0) / b0) * exp(-k2 * (t - t0)))"
    },
    "Ladron_Putsis": {
        "desc": "Modelo de Mercado Potencial Dinámico y Endógeno", "autores": "",
        "eq": "  C(t) = 1.0 - theta * exp(-gamma * N(t) / S), donde M(t) = C(t) * S y la difusión es:\n  dN/dt = (alpha + beta * (N / M)) * (M - N)"
    },
}

new_block_parts = ["\n### 📐 Formulación Matemática de los Modelos Evaluados\n"]
for k, label in MODEL_LABELS.items():
    yr = MODEL_YEARS.get(label, "")
    eq_data = MODEL_EQUATIONS[k]
    autores = eq_data['autores']
    desc = eq_data['desc']
    eq_text = eq_data['eq']
    
    if autores:
        header_content = f"{label} ({autores}, {yr})"
    else:
        header_content = f"{label} ({yr})"
        
    header = "* **" + header_content + "** — " + desc + ":\n"
    new_block_parts.append(header + eq_text)

new_block = "\n  \n".join(new_block_parts) + "\n"

print("--- NEW BLOCK START ---")
print(new_block)
print("--- NEW BLOCK END ---")

print("TEST 1: strip_numeric_prose")
stripped = strip_numeric_prose("## 🤖 6. Informe Analítico Científico RAG\n" + new_block)
print("Stripped size:", len(stripped))
if "2011" not in stripped or "1969" not in stripped:
    print("WARNING: strip_numeric_prose modified the block!")
else:
    print("strip_numeric_prose test OK (numbers retained)")

print("\nTEST 2: check_numeric_prose")
val = ReportValidator("## 🤖 6. Informe Analítico Científico RAG\n" + new_block, [])
val.check_numeric_prose()
print("Issues found by check_numeric_prose:")
for issue in val.issues:
    print(issue.category, "-", issue.evidence)
if not val.issues:
    print("check_numeric_prose test OK (0 hits)")

print("\nDIFF:")
for line in ndiff(original_block.splitlines(), new_block.splitlines()):
    if not line.startswith(' '):
        print(line)
