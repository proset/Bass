import numpy as np
from scipy.optimize import curve_fit
from sklearn.metrics import r2_score
from models.rk4_solver import (
    bass_classic,
    dual_market_bass,
    fourt_woodlock_model,
    gompertz_model,
    generalized_bass_model,
    horsky_simon_model,
    muller_yogev_model,
    vdb_joshi_model,
    logistic_diffusion_convergence,
    ladron_puts_model
)

def calculate_mape(y_true, y_pred):
    """Calcula el Error Porcentual Absoluto Medio (MAPE)."""
    mask = y_true != 0
    if not np.any(mask):
        return 0.0
    return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100.0

def r2_score_manual(y_true, y_pred):
    """Calcula R² de forma robusta manual (evita fallos de sklearn en casos límite)."""
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return 1 - (ss_res / ss_tot) if ss_tot != 0 else 0.0

def estimate_uncertainty_bounds(model_func, t_proj, popt, pcov, bounds=None, num_samples=100):
    """
    Estima las bandas de incertidumbre al 95% usando Simulación de Monte Carlo
    sobre la distribución normal multivariante de los parámetros ajustados.
    """
    if pcov is None or np.all(pcov == 0):
        # Fallback si no hay covarianza
        pred = model_func(t_proj, *popt)
        return pred, pred, pred
        
    try:
        # Generar muestras de parámetros
        samples = np.random.multivariate_normal(popt, pcov, num_samples)
        
        # Filtrar muestras según los límites si están presentes
        if bounds is not None:
            lower_b, upper_b = bounds
            for idx in range(samples.shape[0]):
                samples[idx] = np.clip(samples[idx], lower_b, upper_b)
                
        # Evaluar predicciones para cada muestra
        predictions = []
        for sample in samples:
            try:
                pred = model_func(t_proj, *sample)
                predictions.append(pred)
            except Exception:
                continue
                
        if not predictions:
            # Fallback
            pred = model_func(t_proj, *popt)
            return pred, pred, pred
            
        predictions = np.array(predictions)
        
        # Calcular percentiles 2.5%, 50% y 97.5% per-step
        lower_bound = np.percentile(predictions, 2.5, axis=0)
        median_bound = model_func(t_proj, *popt) # Usar la predicción óptima real como la línea central
        upper_bound = np.percentile(predictions, 97.5, axis=0)
        
        # Asegurar monotonía acumulada lógica en las bandas
        for i in range(1, len(lower_bound)):
            lower_bound[i] = max(lower_bound[i], lower_bound[i-1])
            upper_bound[i] = max(upper_bound[i], upper_bound[i-1])
            
        return lower_bound, median_bound, upper_bound
    except Exception:
        pred = model_func(t_proj, *popt)
        return pred, pred, pred

def bootstrap_uncertainty_bounds(model_func, t_data, n_data, t_proj, popt, bounds=None, n_bootstrap=120):
    """
    Estima las bandas de incertidumbre al 95% usando Bootstrap de Residuos.
    No requiere la matriz de covarianza (pcov): funciona siempre con cualquier
    parámetro, incluso cuando se cargan desde la base de datos.

    Algoritmo:
      1. Calcula los residuos = real - predicho (con popt actual).
      2. En cada iteración, resamplea los residuos y re-ajusta el modelo.
      3. Calcula los percentiles 2.5% y 97.5% sobre todas las proyecciones.
    """
    popt_arr = np.array(popt)

    # Inferir bounds si no están disponibles
    if bounds is None:
        lower_b = np.maximum(popt_arr * 0.001, 0.0)
        upper_b = np.maximum(popt_arr * 200.0, lower_b + 1e-6)
        bounds = (lower_b.tolist(), upper_b.tolist())

    try:
        n_pred_hist = model_func(t_data, *popt_arr)
        residuals = np.array(n_data, dtype=float) - n_pred_hist
    except Exception:
        y_c = model_func(t_proj, *popt_arr)
        return y_c, y_c, y_c

    boot_projections = []
    rng = np.random.default_rng(42)

    for _ in range(n_bootstrap):
        resampled_res = rng.choice(residuals, size=len(residuals), replace=True)
        n_boot = np.clip(n_pred_hist + resampled_res, 0.0, None)
        try:
            popt_boot, _ = curve_fit(
                model_func, t_data, n_boot,
                p0=popt_arr, bounds=bounds, maxfev=5000
            )
            y_boot = model_func(t_proj, *popt_boot)
            if np.all(np.isfinite(y_boot)):
                boot_projections.append(y_boot)
        except Exception:
            continue

    if len(boot_projections) < 10:
        y_c = model_func(t_proj, *popt_arr)
        return y_c, y_c, y_c

    boot_arr = np.array(boot_projections)
    lower = np.percentile(boot_arr, 2.5, axis=0)
    upper = np.percentile(boot_arr, 97.5, axis=0)

    # Garantizar monotonía en acumulados
    for i in range(1, len(lower)):
        lower[i] = max(lower[i], lower[i - 1])
        upper[i] = max(upper[i], upper[i - 1])

    return lower, model_func(t_proj, *popt_arr), upper


def backtest_walk_forward(model_func, t_data, n_data, p0, bounds, maxfev=15000):

    """
    Realiza una validación walk-forward (backtesting): entrena con todos los datos
    menos los últimos 2 años y evalúa el MAPE fuera de muestra de esos 2 años.
    """
    if len(t_data) < 5:
        return np.nan
        
    t_train = t_data[:-2]
    n_train = n_data[:-2]
    
    try:
        if p0 is not None:
            popt, _ = curve_fit(model_func, t_train, n_train, p0=p0, bounds=bounds, maxfev=maxfev)
        else:
            popt, _ = curve_fit(model_func, t_train, n_train, bounds=bounds, maxfev=maxfev)
            
        # Predecir los últimos 2 años
        n_pred_out = model_func(t_data[-2:], *popt)
        return calculate_mape(n_data[-2:], n_pred_out)
    except Exception:
        return np.nan

def fit_all_models(t_data, n_data):
    """
    Ajusta los 7 modelos de difusión a los datos históricos y calcula R², MAPE
    de ajuste y el MAPE de backtesting (validación cruzada).
    """
    if len(t_data) < 5:
        return {}
        
    results = {}
    m_guess = max(n_data) * 1.5
    m_max = max(n_data)
    n_nonzero = np.sum(n_data > 0)
    if n_nonzero <= 2:
        m_limit_mult = 5.0
    elif m_max < 5.0:
        m_limit_mult = 15.0
    else:
        m_limit_mult = 50.0
    
    # 1. Bass Clásico
    bounds_bass = ([0, 1e-8, 1e-8], [m_limit_mult * m_max, 1.0, 1.0])
    p0_bass = [m_guess, 0.01, 0.1]
    try:
        popt, pcov = curve_fit(bass_classic, t_data, n_data, p0=p0_bass, bounds=bounds_bass, maxfev=10000)
        n_pred = bass_classic(t_data, *popt)
        r2 = r2_score_manual(n_data, n_pred)
        mape_fit = calculate_mape(n_data, n_pred)
        mape_val = backtest_walk_forward(bass_classic, t_data, n_data, p0_bass, bounds_bass)
        
        results["Bass_Clasico"] = {
            "popt": popt.tolist(),
            "pcov": pcov.tolist() if pcov is not None else None,
            "bounds": bounds_bass,
            "r_cuadrado": float(r2),
            "mape_ajuste": float(mape_fit),
            "mape_backtest": float(mape_val) if not np.isnan(mape_val) else None,
            "params": {
                "param_m1": float(popt[0]),
                "param_p1": float(popt[1]),
                "param_q1": float(popt[2])
            }
        }
    except Exception:
        pass

    # 2. Dual Market (Multi-Start NLLS)
    bounds_dual = ([0, 1e-6, 0, 0, 1e-6, 0], [m_limit_mult * m_max, 1.0, 1.0, m_limit_mult * m_max, 1.0, 1.0])
    candidate_p0s = [
        [m_max * 0.1, 0.03, 0.38, m_max * 0.9, 0.01, 0.4],
        [m_max * 0.3, 0.02, 0.40, m_max * 0.7, 0.005, 0.3],
        [m_max * 0.5, 0.01, 0.30, m_max * 0.5, 0.01, 0.3],
        [m_max * 0.7, 0.05, 0.50, m_max * 0.3, 0.001, 0.4],
        [m_max * 0.2, 0.04, 0.35, m_max * 0.8, 0.015, 0.45],
        [m_max * 0.4, 0.03, 0.45, m_max * 0.6, 0.008, 0.35]
    ]
    
    best_popt = None
    best_pcov = None
    best_r2 = -np.inf
    best_p0 = None
    
    for p0_cand in candidate_p0s:
        try:
            popt, pcov = curve_fit(dual_market_bass, t_data, n_data, p0=p0_cand, bounds=bounds_dual, maxfev=15000)
            n_pred = dual_market_bass(t_data, *popt)
            r2 = r2_score_manual(n_data, n_pred)
            if r2 > best_r2:
                best_r2 = r2
                best_popt = popt
                best_pcov = pcov
                best_p0 = p0_cand
        except Exception:
            continue
            
    if best_popt is not None:
        n_pred = dual_market_bass(t_data, *best_popt)
        mape_fit = calculate_mape(n_data, n_pred)
        mape_val = backtest_walk_forward(dual_market_bass, t_data, n_data, best_p0, bounds_dual)
        
        results["Dual_Market"] = {
            "popt": best_popt.tolist(),
            "pcov": best_pcov.tolist() if best_pcov is not None else None,
            "bounds": bounds_dual,
            "r_cuadrado": float(best_r2),
            "mape_ajuste": float(mape_fit),
            "mape_backtest": float(mape_val) if not np.isnan(mape_val) else None,
            "params": {
                "param_m1": float(best_popt[0]),
                "param_p1": float(best_popt[1]),
                "param_q1": float(best_popt[2]),
                "param_m2": float(best_popt[3]),
                "param_p2": float(best_popt[4]),
                "param_q2": float(best_popt[5])
            }
        }

    # 3. Fourt & Woodlock (1960) - Innovación Pura
    bounds_fw = ([0.0, 1e-8], [m_limit_mult * m_max, 1.0])
    p0_fw = [m_guess, 0.01]
    try:
        popt, pcov = curve_fit(fourt_woodlock_model, t_data, n_data, p0=p0_fw, bounds=bounds_fw, maxfev=10000)
        n_pred = fourt_woodlock_model(t_data, *popt)
        r2 = r2_score_manual(n_data, n_pred)
        mape_fit = calculate_mape(n_data, n_pred)
        mape_val = backtest_walk_forward(fourt_woodlock_model, t_data, n_data, p0_fw, bounds_fw)
        
        results["Fourt_Woodlock"] = {
            "popt": popt.tolist(),
            "pcov": pcov.tolist() if pcov is not None else None,
            "bounds": bounds_fw,
            "r_cuadrado": float(r2),
            "mape_ajuste": float(mape_fit),
            "mape_backtest": float(mape_val) if not np.isnan(mape_val) else None,
            "params": {
                "param_m1": float(popt[0]),
                "param_p1": float(popt[1])
            }
        }
    except Exception:
        pass

    # 4. Gompertz - Sigmoide Asimétrica
    bounds_gomp = ([0.0, 1e-8, -10.0], [m_limit_mult * m_max, 2.0, 50.0])
    p0_gomp = [m_guess, 0.1, len(t_data) / 2]
    try:
        popt, pcov = curve_fit(gompertz_model, t_data, n_data, p0=p0_gomp, bounds=bounds_gomp, maxfev=10000)
        n_pred = gompertz_model(t_data, *popt)
        r2 = r2_score_manual(n_data, n_pred)
        mape_fit = calculate_mape(n_data, n_pred)
        mape_val = backtest_walk_forward(gompertz_model, t_data, n_data, p0_gomp, bounds_gomp)
        
        results["Gompertz"] = {
            "popt": popt.tolist(),
            "pcov": pcov.tolist() if pcov is not None else None,
            "bounds": bounds_gomp,
            "r_cuadrado": float(r2),
            "mape_ajuste": float(mape_fit),
            "mape_backtest": float(mape_val) if not np.isnan(mape_val) else None,
            "params": {
                "param_m1": float(popt[0]),
                "param_p1": float(popt[1]), # representa k en la BD
                "param_q1": float(popt[2])  # representa t0 en la BD
            }
        }
    except Exception:
        pass

    # 5. Generalized Bass Model (GBM) - Difusión con Shocks de Marketing/Precio
    bounds_gbm = ([0.0, 1e-8, 1e-8, -10.0], [m_limit_mult * m_max, 1.0, 1.0, 10.0])
    p0_gbm = [m_guess, 0.01, 0.1, 0.0]
    try:
        popt, pcov = curve_fit(generalized_bass_model, t_data, n_data, p0=p0_gbm, bounds=bounds_gbm, maxfev=15000)
        n_pred = generalized_bass_model(t_data, *popt)
        r2 = r2_score_manual(n_data, n_pred)
        mape_fit = calculate_mape(n_data, n_pred)
        mape_val = backtest_walk_forward(generalized_bass_model, t_data, n_data, p0_gbm, bounds_gbm)
        
        results["Generalized_Bass"] = {
            "popt": popt.tolist(),
            "pcov": pcov.tolist() if pcov is not None else None,
            "bounds": bounds_gbm,
            "r_cuadrado": float(r2),
            "mape_ajuste": float(mape_fit),
            "mape_backtest": float(mape_val) if not np.isnan(mape_val) else None,
            "params": {
                "param_m1": float(popt[0]),
                "param_p1": float(popt[1]),
                "param_q1": float(popt[2]),
                "param_p2": float(popt[3])  # representa beta en la BD (parámetro de shock)
            }
        }
    except Exception:
        pass

    # 6. Horsky & Simon - Difusión con Publicidad
    bounds_hs = ([0.0, 1e-8, 1e-8, 0.0], [m_limit_mult * m_max, 1.0, 1.0, 1.0])
    p0_hs = [m_guess, 0.01, 0.1, 0.01]
    try:
        popt, pcov = curve_fit(horsky_simon_model, t_data, n_data, p0=p0_hs, bounds=bounds_hs, maxfev=15000)
        n_pred = horsky_simon_model(t_data, *popt)
        r2 = r2_score_manual(n_data, n_pred)
        mape_fit = calculate_mape(n_data, n_pred)
        mape_val = backtest_walk_forward(horsky_simon_model, t_data, n_data, p0_hs, bounds_hs)
        
        results["Horsky_Simon"] = {
            "popt": popt.tolist(),
            "pcov": pcov.tolist() if pcov is not None else None,
            "bounds": bounds_hs,
            "r_cuadrado": float(r2),
            "mape_ajuste": float(mape_fit),
            "mape_backtest": float(mape_val) if not np.isnan(mape_val) else None,
            "params": {
                "param_m1": float(popt[0]),
                "param_p1": float(popt[1]), # representa p0 en la BD
                "param_q1": float(popt[2]), # representa q en la BD
                "param_p2": float(popt[3])  # representa alpha (coeficiente publicitario) en la BD
            }
        }
    except Exception:
        pass

    # 5. Muller & Yogev
    bounds_muller = ([0, 1e-5, 0, 0, 1e-5, 0, 0], [m_limit_mult * m_max, 1.0, 1.0, m_limit_mult * m_max, 1.0, 1.0, 1.0])
    p0_muller = [m_max * 0.2, 0.01, 0.1, m_max * 0.8, 0.005, 0.05, 0.05]
    try:
        popt, pcov = curve_fit(muller_yogev_model, t_data, n_data, p0=p0_muller, bounds=bounds_muller, maxfev=15000)
        n_pred = muller_yogev_model(t_data, *popt)
        r2 = r2_score_manual(n_data, n_pred)
        mape_fit = calculate_mape(n_data, n_pred)
        mape_val = backtest_walk_forward(muller_yogev_model, t_data, n_data, p0_muller, bounds_muller)
        
        results["Muller_Yogev"] = {
            "popt": popt.tolist(),
            "pcov": pcov.tolist() if pcov is not None else None,
            "bounds": bounds_muller,
            "r_cuadrado": float(r2),
            "mape_ajuste": float(mape_fit),
            "mape_backtest": float(mape_val) if not np.isnan(mape_val) else None,
            "params": {
                "param_m1": float(popt[0]),
                "param_p1": float(popt[1]),
                "param_q1": float(popt[2]),
                "param_m2": float(popt[3]),
                "param_p2": float(popt[4]),
                "param_q2": float(popt[5]),
                "param_q12": float(popt[6])
            }
        }
    except Exception:
        pass

    # 6. Van den Bulte & Joshi
    bounds_vdb = ([0, 1e-5, 0, 0, 0, 0.0], [m_limit_mult * m_max, 1.0, 1.0, m_limit_mult * m_max, 1.0, 1.0])
    p0_vdb = [m_max * 0.2, 0.01, 0.1, m_max * 0.8, 0.05, 0.5]
    try:
        popt, pcov = curve_fit(vdb_joshi_model, t_data, n_data, p0=p0_vdb, bounds=bounds_vdb, maxfev=15000)
        n_pred = vdb_joshi_model(t_data, *popt)
        r2 = r2_score_manual(n_data, n_pred)
        mape_fit = calculate_mape(n_data, n_pred)
        mape_val = backtest_walk_forward(vdb_joshi_model, t_data, n_data, p0_vdb, bounds_vdb)
        
        results["VdB_Joshi"] = {
            "popt": popt.tolist(),
            "pcov": pcov.tolist() if pcov is not None else None,
            "bounds": bounds_vdb,
            "r_cuadrado": float(r2),
            "mape_ajuste": float(mape_fit),
            "mape_backtest": float(mape_val) if not np.isnan(mape_val) else None,
            "params": {
                "param_m1": float(popt[0]),
                "param_p1": float(popt[1]),
                "param_q1": float(popt[2]),
                "param_m2": float(popt[3]),
                "param_q2": float(popt[4]),
                "param_p2": float(popt[5])  # representa w en la BD
            }
        }
    except Exception:
        pass

    # 7. Logistic Diffusion-Convergence (Ryu & Kim, 2025)
    try:
        y_max = max(max(n_data), 1e-5)
        y_min = n_data[0] if n_data[0] > 0 else 1.0
        bounds_log = ([y_max, 1e-8, 1e-8, -100.0], [m_limit_mult * y_max, max(y_max, 2e-8), 5.0, len(t_data) * 3])
        p0_log = [y_max * 1.5, np.clip(y_min, 2e-8, y_max * 0.99), 0.1, len(t_data) / 2]
        
        popt, pcov = curve_fit(logistic_diffusion_convergence, t_data, n_data, p0=p0_log, bounds=bounds_log, maxfev=15000)
        n_pred = logistic_diffusion_convergence(t_data, *popt)
        r2 = r2_score_manual(n_data, n_pred)
        mape_fit = calculate_mape(n_data, n_pred)
        mape_val = backtest_walk_forward(logistic_diffusion_convergence, t_data, n_data, p0_log, bounds_log)
        
        results["Logistic_Diffusion_Convergence"] = {
            "popt": popt.tolist(),
            "pcov": pcov.tolist() if pcov is not None else None,
            "bounds": bounds_log,
            "r_cuadrado": float(r2),
            "mape_ajuste": float(mape_fit),
            "mape_backtest": float(mape_val) if not np.isnan(mape_val) else None,
            "params": {
                "param_m1": float(popt[0]),  # b1
                "param_p1": float(popt[1]),  # b0
                "param_q1": float(popt[2]),  # k2
                "param_p2": float(popt[3])   # t0
            }
        }
    except Exception:
        pass

    # 8. Ladrón-de-Guevara & Putsis (2011) - Mercado Potencial Dinámico
    try:
        bounds_lgp = ([0, 1e-8, 0.0, 0.0, 0.0], [m_limit_mult * m_max, 1.0, 1.0, 1.0, 10.0])
        p0_lgp = [m_max * 1.5, 0.01, 0.1, 0.5, 1.0]
        
        popt, pcov = curve_fit(ladron_puts_model, t_data, n_data, p0=p0_lgp, bounds=bounds_lgp, maxfev=15000)
        n_pred = ladron_puts_model(t_data, *popt)
        r2 = r2_score_manual(n_data, n_pred)
        mape_fit = calculate_mape(n_data, n_pred)
        mape_val = backtest_walk_forward(ladron_puts_model, t_data, n_data, p0_lgp, bounds_lgp)
        
        results["Ladron_Putsis"] = {
            "popt": popt.tolist(),
            "pcov": pcov.tolist() if pcov is not None else None,
            "bounds": bounds_lgp,
            "r_cuadrado": float(r2),
            "mape_ajuste": float(mape_fit),
            "mape_backtest": float(mape_val) if not np.isnan(mape_val) else None,
            "params": {
                "param_m1": float(popt[0]),  # S (sistema social)
                "param_p1": float(popt[1]),  # alpha (influencia externa)
                "param_q1": float(popt[2]),  # beta (influencia interna)
                "param_m2": float(popt[3]),  # theta (fracción inicial)
                "param_p2": float(popt[4])   # gamma (efecto de red directo)
            }
        }
    except Exception:
        pass

    return results

def rank_and_select_best_model(results):
    """
    Ordena y selecciona el mejor modelo según una puntuación combinada
    de R² y MAPE de Ajuste, priorizando R² y penalizando modelos que no convergieron
    o que presentan límites de saturación físicamente absurdos (sobreajuste explosivo).
    """
    if not results:
        return None, []
        
    ranked_list = []
    for model_name, metrics in results.items():
        r2 = metrics.get("r_cuadrado", -999.0)
        mape = metrics.get("mape_ajuste", 999.0)
        mape_bt = metrics.get("mape_backtest", 999.0)
        
        # Obtener param_m1 y param_m2 para calcular el límite de mercado total
        p_dict = metrics.get("params", metrics)
        try:
            m1 = float(p_dict.get("param_m1", 0.0))
        except (ValueError, TypeError):
            m1 = 0.0
            
        try:
            m2 = float(p_dict.get("param_m2", 0.0))
        except (ValueError, TypeError):
            m2 = 0.0
            
        m_total = m1 + m2
        
        # Penalizar si el potencial de mercado es físicamente absurdo (>12,000 millones de adoptantes)
        # o si tiene un comportamiento explosivo inverosímil.
        penalty = 0.0
        # Inferir m_max a partir de los bounds del modelo
        m_max_inf = 1.0
        if "bounds" in metrics and metrics["bounds"] is not None:
            b_upper = metrics["bounds"][1]
            if len(b_upper) >= 1:
                # Si el bound superior es m_limit_mult * m_max, podemos inferir m_max.
                # Como los bounds se guardaron con m_limit_mult * m_max, y m_limit_mult es 15 o 50,
                # podemos estimar m_max de forma aproximada o exacta.
                # Aquí, b_upper[0] es la cota superior del primer parámetro (m1).
                # Si la cota superior es muy grande, estimamos m_max_inf.
                m_max_inf = float(b_upper[0]) / 15.0  # asuncion conservadora
        
        if m_total > 12000.0:
            penalty = 80.0  # Penalización severa para descartar el modelo del ranking principal
        elif m_total > 8000.0:
            penalty = 40.0  # Penalización moderada
            
        # Penalización por saturación explosiva irreal en fases de lanzamiento
        # Si la adopción máxima histórica inferida (m_max_inf) es pequeña (tecnología naciente),
        # un límite de mercado (m_total) que sea más de 20 veces m_max_inf es extremadamente inestable.
        if m_max_inf < 5.0 and m_total > 20.0 * m_max_inf:
            penalty += 60.0
            
        # Puntuación combinada (mayor R2 y menor MAPE es mejor)
        # R2 tiene un peso del 70%, MAPE de ajuste 15% y MAPE de backtest 15%
        mape_score = 100.0 - min(mape, 100.0)
        mape_bt_score = 100.0 - min(mape_bt if mape_bt is not None else mape, 100.0)
        
        score = (r2 * 70.0) + (mape_score * 0.15) + (mape_bt_score * 0.15) - penalty
        
        ranked_list.append({
            "model_name": model_name,
            "score": score,
            "r_cuadrado": r2,
            "mape_ajuste": mape,
            "mape_backtest": mape_bt,
            "m_total": m_total
        })
        
    ranked_list = sorted(ranked_list, key=lambda x: x["score"], reverse=True)
    best_model = ranked_list[0]["model_name"] if ranked_list else None
    return best_model, ranked_list
