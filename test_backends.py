"""Test de la capa semantica multi-backend (Gemini/Claude) sobre el informe
final de una tecnologia. Uso: python test_backends.py <backend> [tech]
Ejemplos:
  python test_backends.py gemini netflix
  python test_backends.py claude chatgpt
Sin tech: default chatgpt (compatibilidad)."""
import sys
sys.path.insert(0, r"C:\Users\roset\Bass")

from llm_reviewer import full_review, gate
from data.loaders import load_historical_data, load_model_parameters
from report_validator import ModelFit

TECH = sys.argv[2] if len(sys.argv) > 2 else "chatgpt"
print(f"[test_backends] Tecnologia: {TECH} | Backend: {sys.argv[1] if len(sys.argv) > 1 else 'gemini'}")

# model_labels es local al orquestador — copia literal del parche G
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


def run_test(backend):
    df = load_historical_data(TECH)
    params = load_model_parameters(TECH)
    anios = df["anio"].tolist()
    y_true = df["adopcion_acumulada"].tolist()
    real_series = {int(a): float(v) for a, v in zip(anios, y_true)}

    model_fits = []
    for m_key, label in MODEL_LABELS.items():
        if m_key not in params:
            continue
        p = params[m_key]
        model_fits.append(ModelFit(
            name=label,
            r2=float(p.get("r_cuadrado") or 0),
            mape=float(p.get("mape_ajuste") or 999),
            projections={},
        ))

    with open(f"informe_global_{TECH}.md", encoding="utf-8") as f:
        informe = f.read()

    print(f"=== TEST {backend.upper()} ===")
    issues = full_review(informe, real_series, model_fits,
                         backend=backend, use_llm=True)
    blockers = [i for i in issues if i.severity == "BLOCKER"]
    warnings = [i for i in issues if i.severity == "WARNING"]
    print(f"Total issues: {len(issues)} | BLOCKERs: {len(blockers)} | WARNINGs: {len(warnings)}")
    for b in blockers:
        print(f"  [BLOCKER] {b.category}: {b.message[:120]}")
    print(f"GATE: {gate(issues)}")
    print()


if __name__ == "__main__":
    backend_arg = sys.argv[1] if len(sys.argv) > 1 else "gemini"
    run_test(backend_arg)
