"""
models/analytical_projections.py — Soluciones analíticas para proyección.
Reemplaza RK4 en proyecciones (RK4 se queda para fitting).
Las fórmulas analíticas nunca producen NaN.
"""
import numpy as np

def project_bass(p, q, m, t_array):
    """Bass analítica: N(t) = m * (1 - exp(-(p+q)*t)) / (1 + (q/p) * exp(-(p+q)*t))"""
    if p == 0:
        # Límite cuando p→0: N(t) = m * (1 - exp(-q*t))  (solo imitadores)
        return m * (1 - np.exp(-q * t_array))
    pq = p + q
    exp_term = np.exp(-pq * t_array)
    return m * (1 - exp_term) / (1 + (q / p) * exp_term)

def project_dual_market(p1, q1, m1, p2, q2, m2, t_array):
    """Dual Market: suma de dos Bass analíticas"""
    return project_bass(p1, q1, m1, t_array) + project_bass(p2, q2, m2, t_array)

def project_gompertz(m, k, t0, t_array):
    """Gompertz: N(t) = m * exp(-exp(-k*(t-t0)))"""
    return m * np.exp(-np.exp(-k * (t_array - t0)))

def project_fourt_woodlock(m, p, t_array):
    """Fourt & Woodlock: N(t) = m * (1 - exp(-p*t))"""
    return m * (1 - np.exp(-p * t_array))

def project_logistic_convergence(b1, b0, k2, t0, t_array):
    """R&K (logística): N(t) = b1 / (1 + ((b1-b0)/b0) * exp(-k2*(t-t0)))"""
    if b0 == 0:
        b0 = 1e-10  # evitar división por cero
    return b1 / (1 + ((b1 - b0) / b0) * np.exp(-k2 * (t_array - t0)))

def project_gbm(p, q, m, beta, t_array):
    """
    GBM: Bass con factor (1 + beta*t).
    Solución aproximada: N(t) ≈ N_bass(t) * (1 + beta*t / (1 + beta*t_max))
    Si beta=0 → Bass estándar.
    """
    n_bass = project_bass(p, q, m, t_array)
    if beta == 0:
        return n_bass
    # Factor de crecimiento adicional (aproximación estable)
    factor = 1 + beta * t_array / (1 + abs(beta) * t_array[-1])
    return n_bass * factor

def project_horsky_simon(p0, alpha, q, m, t_array):
    """
    Horsky & Simon: Bass con término ln(1+t).
    Aproximación: usar Bass analítica con p efectivo = p0 + alpha*ln(1+t).
    """
    # p efectivo varía con t — usar Bass con p promedio
    p_eff = p0 + alpha * np.log(1 + t_array)
    # Bass con p variable (aproximación)
    if q == 0:
        return m * (1 - np.exp(-p_eff * t_array))
    
    # Para cada t, calcular Bass con p_eff(t)
    results = np.zeros_like(t_array, dtype=float)
    for i, t in enumerate(t_array):
        p = p_eff[i] if p_eff[i] > 0 else 1e-10
        exp_term = np.exp(-(p + q) * t)
        results[i] = m * (1 - exp_term) / (1 + (q / p) * exp_term)
    return results

def project_vdb_joshi(m1, p1, q1, m2, p2, q2, w, t_array):
    """VdB: suma ponderada de dos Bass"""
    n1 = project_bass(p1, q1, m1, t_array)
    n2 = project_bass(p2, q2, m2, t_array)
    if w is None:
        w = 0.5
    return w * n1 + (1 - w) * n2

def project_muller_yogev(ni, pi, qi, nm, pm, qm, t_array):
    """Muller & Yogev: dos Bass (innovadores + imitadores)"""
    return project_bass(pi, qi, ni, t_array) + project_bass(pm, qm, nm, t_array)

def project_ladron_putsis(S, theta, gamma, p, q, t_array, n0=0):
    """
    Ladrón: mercado dinámico (ODE — sin analítica simple).
    Fallback: usar Bass con m=S (mercado potencial total).
    """
    # Aproximación: Bass con mercado potencial S
    return project_bass(p, q, S, t_array)


# === DISPATCHER ===
def project_model(model_key, params, t_array):
    """
    Dispatch a la función analítica correcta según el modelo.
    params: dict con los parámetros del modelo (de model_parameters).
    t_array: array de años relativos (t=0 en el primer año de la serie).
    Retorna: array de proyecciones (nunca NaN).
    """
    p1 = params.get("param_p1", 0)
    q1 = params.get("param_q1", 0)
    m1 = params.get("param_m1", 0)
    p2 = params.get("param_p2", 0)
    q2 = params.get("param_q2", 0)
    m2 = params.get("param_m2", 0)
    q12 = params.get("param_q12", 0)
    
    if model_key == "Bass_Clasico":
        return project_bass(p1, q1, m1, t_array)
    
    elif model_key == "Dual_Market":
        return project_dual_market(p1, q1, m1, p2, q2, m2, t_array)
    
    elif model_key == "Gompertz":
        # gompertz_model(t, m, k, t0) -> reconstruct_popt = [m1, p1, q1]
        # Por tanto: m = m1, k = p1, t0 = q1
        return project_gompertz(m1, p1, q1, t_array)
    
    elif model_key == "Fourt_Woodlock":
        # fourt_woodlock_model(t, m, p) -> reconstruct_popt = [m1, p1]
        return project_fourt_woodlock(m1, p1, t_array)
    
    elif model_key == "Logistic_Diffusion_Convergence":
        # logistic_diffusion_convergence(t, b1, b0, k2, t0) -> reconstruct_popt = [m1, p1, q1, p2]
        # b1 = m1, b0 = p1, k2 = q1, t0 = p2
        return project_logistic_convergence(m1, p1, q1, p2, t_array)
    
    elif model_key == "Generalized_Bass":
        # generalized_bass_model(t, m, p, q, beta) -> reconstruct_popt = [m1, p1, q1, p2]
        # m = m1, p = p1, q = q1, beta = p2
        return project_gbm(p1, q1, m1, p2, t_array)
    
    elif model_key == "Horsky_Simon":
        # horsky_simon_model(t, m, p0, q, alpha) -> reconstruct_popt = [m1, p1, q1, p2]
        # m = m1, p0 = p1, q = q1, alpha = p2
        return project_horsky_simon(p1, p2, q1, m1, t_array)
    
    elif model_key == "VdB_Joshi":
        # vdb_joshi_model(t, M1, p1, q1, M2, q2, w) -> reconstruct_popt = [m1, p1, q1, m2, q2, p2]
        # M1 = m1, p1 = p1, q1 = q1, M2 = m2, q2 = q2, w = p2
        return project_vdb_joshi(m1, p1, q1, m2, 0, q2, p2, t_array) 
        # NOTA: p2 de VdB es `w`, p2 de la DB es w. En rk4 la función no usa p2 en el 2do bass, usa solo q2. Pasamos 0 a p2 del bass2.
    
    elif model_key == "Muller_Yogev":
        # muller_yogev_model(t, Ni, pi, qi, Nm, pm, qm, qim) -> reconstruct_popt = [m1, p1, q1, m2, p2, q2, q12]
        # Ni = m1, pi = p1, qi = q1, Nm = m2, pm = p2, qm = q2, qim = q12
        return project_muller_yogev(m1, p1, q1, m2, p2, q2, t_array)
    
    elif model_key == "Ladron_Putsis":
        # ladron_puts_model(t, S, alpha, beta, theta, gamma) -> reconstruct_popt = [m1, p1, q1, m2, p2]
        # S = m1, alpha = p1, beta = q1, theta = m2, gamma = p2
        return project_ladron_putsis(m1, m2, p2, p1, q1, t_array)
    
    else:
        # Fallback: Bass simple
        return project_bass(p1, q1, m1, t_array)
