import os
import toml
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
import psycopg2

def r2_score_manual(y_true, y_pred):
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

try:
    secrets = toml.load(os.path.join(".streamlit", "secrets.toml"))
    conn_params = secrets["postgres"]
except Exception:
    conn_params = {
        "host": os.environ.get("PG_HOST"),
        "database": os.environ.get("PG_DATABASE", "postgres"),
        "user": os.environ.get("PG_USER"),
        "password": os.environ.get("PG_PASSWORD"),
        "port": int(os.environ.get("PG_PORT", 6543))
    }

def bass_classic(t, m, p, q):
    p = max(p, 1e-8)
    exp_term = np.exp(-(p + q) * t)
    numerator = m * (1 - exp_term)
    denominator = 1 + (q / p) * exp_term
    return numerator / denominator

def dual_market_bass(t, m1, p1, q1, m2, p2, q2):
    return bass_classic(t, m1, p1, q1) + bass_classic(t, m2, p2, q2)

def logistic_diffusion_convergence(t, b1, b0, k2, t0):
    b0 = max(b0, 1e-8)
    b1 = max(b1, b0 + 1e-8)
    k2 = max(k2, 1e-8)
    exponent = -k2 * (t - t0)
    exponent = np.clip(exponent, -700, 700)
    denom = 1 + ((b1 - b0) / b0) * np.exp(exponent)
    return b1 / denom

# ==========================================
# Resolvedor Numérico RK4 y Modelos de Difusión Científicos
# ==========================================
def integrate_rk4(f, y0, t_grid, steps_per_unit=10):
    y = np.zeros(len(t_grid))
    y[0] = y0
    
    for idx in range(len(t_grid) - 1):
        t_start = t_grid[idx]
        t_end = t_grid[idx+1]
        dt = (t_end - t_start) / steps_per_unit
        
        current_y = y[idx]
        for _ in range(steps_per_unit):
            t = t_start + _ * dt
            k1 = f(t, current_y)
            k2 = f(t + dt/2, current_y + dt*k1/2)
            k3 = f(t + dt/2, current_y + dt*k2/2)
            k4 = f(t + dt, current_y + dt*k3)
            current_y += dt * (k1 + 2*k2 + 2*k3 + k4) / 6
            
        y[idx+1] = current_y
    return y

def tanny_derzko_model(t, n1, p1, n2, p2, q2):
    n = max(n1 + n2, 1e-8)
    p1 = max(p1, 1e-8)
    p2 = max(p2, 1e-8)
    q2 = max(q2, 0.0)
    
    t_grid = np.arange(int(max(t)) + 1)
    x1_grid = n1 * (1.0 - np.exp(-p1 * t_grid))
    
    def f(time, x2):
        x1_val = n1 * (1.0 - np.exp(-p1 * time))
        val = (p2 + q2 * (x1_val + x2) / n) * (n2 - x2)
        return max(val, 0.0)
        
    x2_grid = integrate_rk4(f, 0.0, t_grid)
    total_grid = x1_grid + x2_grid
    return total_grid[np.round(t).astype(int)]

def steffens_murthy_model(t, K1, alpha, beta, K2, gamma):
    alpha = max(alpha, 1e-8)
    beta = max(beta, 0.0)
    gamma = max(gamma, 0.0)
    
    t_grid = np.arange(int(max(t)) + 1)
    N1_grid = bass_classic(t_grid, K1, alpha, beta)
    
    def f(time, N2):
        N1_val = bass_classic(time, K1, alpha, beta)
        val = (K2 - N2) * gamma * (N1_val + N2)
        return max(val, 0.0)
        
    N2_grid = integrate_rk4(f, 0.0, t_grid)
    total_grid = N1_grid + N2_grid
    return total_grid[np.round(t).astype(int)]

def muller_yogev_model(t, Ni, pi, qi, Nm, pm, qm, qim):
    pi = max(pi, 1e-8)
    qi = max(qi, 0.0)
    pm = max(pm, 1e-8)
    qm = max(qm, 0.0)
    qim = max(qim, 0.0)
    
    t_grid = np.arange(int(max(t)) + 1)
    I_grid = bass_classic(t_grid, Ni, pi, qi)
    denom = max(Ni + Nm, 1e-8)
    
    def f(time, M):
        I_val = bass_classic(time, Ni, pi, qi)
        val = (pm + qm * M / denom + qim * I_val / denom) * (Nm - M)
        return max(val, 0.0)
        
    M_grid = integrate_rk4(f, 0.0, t_grid)
    total_grid = I_grid + M_grid
    return total_grid[np.round(t).astype(int)]

def vdb_joshi_model(t, M1, p1, q1, M2, q2, w):
    p1 = max(p1, 1e-8)
    q1 = max(q1, 0.0)
    q2 = max(q2, 0.0)
    w = np.clip(w, 0.0, 1.0)
    
    t_grid = np.arange(int(max(t)) + 1)
    F1_grid = bass_classic(t_grid, 1.0, p1, q1)
    
    def f(time, F2):
        F1_val = bass_classic(time, 1.0, p1, q1)
        val = q2 * (w * F1_val + (1.0 - w) * F2) * (1.0 - F2)
        return max(val, 0.0)
        
    F2_grid = integrate_rk4(f, 0.0, t_grid)
    total_grid = M1 * F1_grid + M2 * F2_grid
    return total_grid[np.round(t).astype(int)]

def fit_models_for_technology(tech_name, df):
    t_data = np.arange(len(df))
    n_data = df["adopcion_acumulada"].values

    if len(t_data) < 5:
        print(f"[{tech_name}] Insuficientes datos para modelar.")
        return None

    results = {}
    m_guess = max(n_data) * 2
    bounds_bass = ([0, 1e-5, 1e-5], [np.inf, 1.0, 1.0])
    p0_bass = [m_guess, 0.01, 0.1]
    
    try:
        popt_bass, _ = curve_fit(bass_classic, t_data, n_data, p0=p0_bass, bounds=bounds_bass, maxfev=10000)
        n_pred_bass = bass_classic(t_data, *popt_bass)
        r2_bass = r2_score_manual(n_data, n_pred_bass)
        results["Bass_Clasico"] = {
            "param_m1": float(popt_bass[0]),
            "param_p1": float(popt_bass[1]),
            "param_q1": float(popt_bass[2]),
            "r_cuadrado": float(r2_bass)
        }
    except Exception as e:
        print(f"[{tech_name}] Error ajustando Bass Clásico: {e}")

    best_popt = None
    best_r2 = -np.inf
    m_max = max(n_data)
    
    # Rejilla multi-start para evitar convergencia en mínimos locales
    candidate_p0s = [
        [m_max * 0.1, 0.03, 0.38, m_max * 0.9, 0.01, 0.4],
        [m_max * 0.3, 0.02, 0.40, m_max * 0.7, 0.005, 0.3],
        [m_max * 0.5, 0.01, 0.30, m_max * 0.5, 0.01, 0.3],
        [m_max * 0.7, 0.05, 0.50, m_max * 0.3, 0.001, 0.4],
        [m_max * 0.2, 0.04, 0.35, m_max * 0.8, 0.015, 0.45],
        [m_max * 0.4, 0.03, 0.45, m_max * 0.6, 0.008, 0.35]
    ]
    
    bounds_dual = ([0, 1e-6, 0, 0, 1e-6, 0], [np.inf, 1.0, 1.0, np.inf, 1.0, 1.0])
    
    for p0_cand in candidate_p0s:
        try:
            popt_cand, _ = curve_fit(dual_market_bass, t_data, n_data, p0=p0_cand, bounds=bounds_dual, maxfev=15000)
            r2_cand = r2_score_manual(n_data, dual_market_bass(t_data, *popt_cand))
            if r2_cand > best_r2:
                best_r2 = r2_cand
                best_popt = popt_cand
        except Exception:
            continue
            
    if best_popt is not None:
        results["Dual_Market"] = {
            "param_m1": float(best_popt[0]),
            "param_p1": float(best_popt[1]),
            "param_q1": float(best_popt[2]),
            "param_m2": float(best_popt[3]),
            "param_p2": float(best_popt[4]),
            "param_q2": float(best_popt[5]),
            "r_cuadrado": float(best_r2)
        }
    else:
        print(f"[{tech_name}] No se pudo ajustar el modelo Dual Market.")

    # 1. Tanny & Derzko
    try:
        bounds_tanny = ([0, 1e-5, 0, 1e-5, 0], [np.inf, 1.0, np.inf, 1.0, 1.0])
        p0_tanny = [m_guess * 0.2, 0.01, m_guess * 0.8, 0.005, 0.1]
        popt_tanny, _ = curve_fit(tanny_derzko_model, t_data, n_data, p0=p0_tanny, bounds=bounds_tanny, maxfev=20000)
        n_pred_tanny = tanny_derzko_model(t_data, *popt_tanny)
        r2_tanny = r2_score_manual(n_data, n_pred_tanny)
        results["Tanny_Derzko"] = {
            "param_m1": float(popt_tanny[0]),
            "param_p1": float(popt_tanny[1]),
            "param_m2": float(popt_tanny[2]),
            "param_p2": float(popt_tanny[3]),
            "param_q2": float(popt_tanny[4]),
            "r_cuadrado": float(r2_tanny)
        }
    except Exception as e:
        print(f"[{tech_name}] Error ajustando Tanny & Derzko: {e}")

    # 2. Steffens & Murthy
    try:
        bounds_steffens = ([0, 1e-5, 0, 0, 0], [np.inf, 1.0, 1.0, np.inf, 1.0])
        p0_steffens = [m_guess * 0.2, 0.01, 0.1, m_guess * 0.8, 0.05]
        popt_steffens, _ = curve_fit(steffens_murthy_model, t_data, n_data, p0=p0_steffens, bounds=bounds_steffens, maxfev=20000)
        n_pred_steffens = steffens_murthy_model(t_data, *popt_steffens)
        r2_steffens = r2_score_manual(n_data, n_pred_steffens)
        results["Steffens_Murthy"] = {
            "param_m1": float(popt_steffens[0]),
            "param_p1": float(popt_steffens[1]),
            "param_q1": float(popt_steffens[2]),
            "param_m2": float(popt_steffens[3]),
            "param_q2": float(popt_steffens[4]),
            "r_cuadrado": float(r2_steffens)
        }
    except Exception as e:
        print(f"[{tech_name}] Error ajustando Steffens & Murthy: {e}")

    # 3. Muller & Yogev
    try:
        bounds_muller = ([0, 1e-5, 0, 0, 1e-5, 0, 0], [np.inf, 1.0, 1.0, np.inf, 1.0, 1.0, 1.0])
        p0_muller = [m_guess * 0.2, 0.01, 0.1, m_guess * 0.8, 0.005, 0.05, 0.05]
        popt_muller, _ = curve_fit(muller_yogev_model, t_data, n_data, p0=p0_muller, bounds=bounds_muller, maxfev=20000)
        n_pred_muller = muller_yogev_model(t_data, *popt_muller)
        r2_muller = r2_score_manual(n_data, n_pred_muller)
        results["Muller_Yogev"] = {
            "param_m1": float(popt_muller[0]),
            "param_p1": float(popt_muller[1]),
            "param_q1": float(popt_muller[2]),
            "param_m2": float(popt_muller[3]),
            "param_p2": float(popt_muller[4]),
            "param_q2": float(popt_muller[5]),
            "param_q12": float(popt_muller[6]),
            "r_cuadrado": float(r2_muller)
        }
    except Exception as e:
        print(f"[{tech_name}] Error ajustando Muller & Yogev: {e}")

    # 4. Van den Bulte & Joshi
    try:
        bounds_vdb = ([0, 1e-5, 0, 0, 0, 0.0], [np.inf, 1.0, 1.0, np.inf, 1.0, 1.0])
        p0_vdb = [m_guess * 0.2, 0.01, 0.1, m_guess * 0.8, 0.05, 0.5]
        popt_vdb, _ = curve_fit(vdb_joshi_model, t_data, n_data, p0=p0_vdb, bounds=bounds_vdb, maxfev=20000)
        n_pred_vdb = vdb_joshi_model(t_data, *popt_vdb)
        r2_vdb = r2_score_manual(n_data, n_pred_vdb)
        results["VdB_Joshi"] = {
            "param_m1": float(popt_vdb[0]),
            "param_p1": float(popt_vdb[1]),
            "param_q1": float(popt_vdb[2]),
            "param_m2": float(popt_vdb[3]),
            "param_q2": float(popt_vdb[4]),
            "param_p2": float(popt_vdb[5]),
            "r_cuadrado": float(r2_vdb)
        }
    except Exception as e:
        print(f"[{tech_name}] Error ajustando Van den Bulte & Joshi: {e}")

    # 5. Logistic Diffusion-Convergence (Ryu & Kim, 2025)
    try:
        y_max = max(max(n_data), 1e-5)
        y_min = n_data[0] if n_data[0] > 0 else 1.0
        bounds_log = ([y_max, 1e-8, 1e-8, -100.0], [np.inf, max(y_max, 2e-8), 5.0, len(t_data) * 3])
        p0_log = [y_max * 1.5, np.clip(y_min, 2e-8, y_max * 0.99), 0.1, len(t_data) / 2]
        
        popt_log, _ = curve_fit(logistic_diffusion_convergence, t_data, n_data, p0=p0_log, bounds=bounds_log, maxfev=15000)
        n_pred_log = logistic_diffusion_convergence(t_data, *popt_log)
        r2_log = r2_score_manual(n_data, n_pred_log)
        results["Logistic_Diffusion_Convergence"] = {
            "param_m1": float(popt_log[0]),  # b1
            "param_p1": float(popt_log[1]),  # b0
            "param_q1": float(popt_log[2]),  # k2
            "param_p2": float(popt_log[3]),  # t0
            "r_cuadrado": float(r2_log)
        }
    except Exception as e:
        print(f"[{tech_name}] Error ajustando Logistic Diffusion-Convergence: {e}")

    return results

def main():
    print("Iniciando Dual Market Solver...")
    
    try:
        conn = psycopg2.connect(**conn_params)
        conn.autocommit = True
        cursor = conn.cursor()
    except Exception as e:
        print(f"Error conectando a la base de datos: {e}")
        return
        
    query = "SELECT * FROM historical_adoption ORDER BY anio"
    df_full = pd.read_sql(query, conn)
    
    if df_full.empty:
        print("No se encontraron datos en historical_adoption.")
        return

    tecnologias = df_full["tecnologia"].unique()

    for tech in tecnologias:
        print(f"\n--- Procesando: {tech} ---")
        df_tech = df_full[df_full["tecnologia"] == tech].copy()
        
        fits = fit_models_for_technology(tech, df_tech)
        
        if fits:
            for modelo_tipo, params in fits.items():
                print(f"Guardando resultados para {modelo_tipo} (R2: {params.get('r_cuadrado', 0):.4f})")
                
                cursor.execute("DELETE FROM model_parameters WHERE tecnologia = %s AND modelo_tipo = %s", (tech, modelo_tipo))
                
                cols = ["tecnologia", "modelo_tipo"] + list(params.keys())
                vals = [tech, modelo_tipo] + list(params.values())
                placeholders = ", ".join(["%s"] * len(vals))
                
                insert_q = f"INSERT INTO model_parameters ({', '.join(cols)}) VALUES ({placeholders})"
                cursor.execute(insert_q, vals)

    print("\nProceso de modelado finalizado con éxito.")
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
