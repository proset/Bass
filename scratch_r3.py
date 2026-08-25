import sys
import os
sys.path.append(os.path.abspath("C:/Users/roset/Bass"))
from data.report_compiler import strip_numeric_prose

original = r"""
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

print("Testing original block:")
stripped = strip_numeric_prose("## 🤖 6. Informe Analítico Científico RAG\n" + original)
if stripped != "## 🤖 6. Informe Analítico Científico RAG\n" + original:
    print("WARNING: original block modified!")
    import difflib
    print('\n'.join(difflib.ndiff(("## 🤖 6. Informe Analítico Científico RAG\n" + original).splitlines(), stripped.splitlines())))
else:
    print("Original block intact.")
