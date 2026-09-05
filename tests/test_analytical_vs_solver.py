import sys
import os
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from models.analytical_projections import project_model
from models.rk4_solver import (
    bass_classic, dual_market_bass, fourt_woodlock_model, gompertz_model,
    generalized_bass_model, horsky_simon_model, muller_yogev_model,
    vdb_joshi_model, logistic_diffusion_convergence, ladron_puts_model
)
from data.loaders import load_model_parameters

def rebuild_popt(model_name, params_dict):
    keys = {
        "Bass_Clasico": ["param_m1", "param_p1", "param_q1"],
        "Dual_Market": ["param_m1", "param_p1", "param_q1", "param_m2", "param_p2", "param_q2"],
        "Fourt_Woodlock": ["param_m1", "param_p1"],
        "Gompertz": ["param_m1", "param_p1", "param_q1"],
        "Logistic_Diffusion_Convergence": ["param_m1", "param_p1", "param_q1", "param_p2"],
        "Generalized_Bass": ["param_m1", "param_p1", "param_q1", "param_p2"],
        "Horsky_Simon": ["param_m1", "param_p1", "param_q1", "param_p2"],
        "VdB_Joshi": ["param_m1", "param_p1", "param_q1", "param_m2", "param_q2", "param_p2"],
        "Muller_Yogev": ["param_m1", "param_p1", "param_q1", "param_m2", "param_p2", "param_q2", "param_q12"],
        "Ladron_Putsis": ["param_m1", "param_p1", "param_q1", "param_m2", "param_p2"]
    }
    return [float(params_dict[k]) for k in keys[model_name]]

SOLVERS = {
    "Bass_Clasico": bass_classic,
    "Dual_Market": dual_market_bass,
    "Fourt_Woodlock": fourt_woodlock_model,
    "Gompertz": gompertz_model,
    "Generalized_Bass": generalized_bass_model,
    "Horsky_Simon": horsky_simon_model,
    "Muller_Yogev": muller_yogev_model,
    "VdB_Joshi": vdb_joshi_model,
    "Logistic_Diffusion_Convergence": logistic_diffusion_convergence,
    "Ladron_Putsis": ladron_puts_model,
}

TECHS = ["tesla", "instagram", "mounjaro", "ozempic", "vehiculos electricos chinos", "gemini"]

def test_analytical_matches_solver():
    """
    Fix 42: invariante permanente — project_model debe reproducir el solver.
    Cualquier modelo que diverja >1M falla este test (nuevo modelo con analítica
    aproximada será cazado aquí).
    """
    print("=" * 70)
    print("TEST: AUDITORÍA ANALÍTICA vs SOLVER RK4")
    print("=" * 70)

    for tech in TECHS:
        params = load_model_parameters(tech)
        if not params:
            continue

        t = np.arange(11, dtype=float)
        print(f"\n--- Probando tech: {tech} ---")
        
        for model_key, solver_fn in SOLVERS.items():
            if model_key not in params:
                continue
            m = params[model_key]
            
            y_analytic = project_model(model_key, m, t)
            
            popt = rebuild_popt(model_key, m)
            y_solver = solver_fn(t, *popt)
                
            mask = ~np.isnan(y_solver) if hasattr(y_solver, '__len__') else None
            if mask is not None:
                diffs = np.abs(np.asarray(y_analytic)[mask] - np.asarray(y_solver)[mask])
                max_diff = diffs.max() if len(diffs) else 0
            else:
                max_diff = abs(y_analytic - y_solver)
                
            print(f"  {model_key:35s} max_diff = {max_diff:8.2f}M")
            assert max_diff <= 1.0, f"ERROR: {model_key} diverge {max_diff}M en {tech} — enrutar a RK4"

    print("\n" + "=" * 70)
    print("[OK] TEST PASADO: Todos los modelos reproducen el solver (diff <= 1M)")
    print("=" * 70)

if __name__ == "__main__":
    test_analytical_matches_solver()
