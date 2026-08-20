import numpy as np

def bass_classic(t, m, p, q):
    """
    Modelo de Bass Clásico (1969)
    """
    p = max(p, 1e-8)
    exp_term = np.exp(-(p + q) * t)
    numerator = m * (1 - exp_term)
    denominator = 1 + (q / p) * exp_term
    return numerator / denominator

def dual_market_bass(t, m1, p1, q1, m2, p2, q2):
    """
    Modelo de Dos Mercados Independientes (Roset & Canals, 2011)
    """
    return bass_classic(t, m1, p1, q1) + bass_classic(t, m2, p2, q2)

def logistic_diffusion_convergence(t, b1, b0, k2, t0):
    """
    Modelo Logístico de Convergencia
    """
    b0 = max(b0, 1e-8)
    b1 = max(b1, b0 + 1e-8)
    k2 = max(k2, 1e-8)
    exponent = -k2 * (t - t0)
    exponent = np.clip(exponent, -700, 700)
    denom = 1 + ((b1 - b0) / b0) * np.exp(exponent)
    return b1 / denom

# ==========================================
# Resolvedor Numérico RK4 y Modelos de Difusión Científicos (EDO)
# ==========================================
def integrate_rk4(f, y0, t_grid, steps_per_unit=10):
    """
    Implementación del Resolvedor Numérico Runge-Kutta de 4º Orden (RK4)
    f: función f(t, y) que devuelve dy/dt
    y0: condición inicial y(0)
    t_grid: vector de tiempo discretizado (generalmente números enteros de años)
    """
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

def fourt_woodlock_model(t, m, p):
    """
    Modelo de Fourt & Woodlock (1960) - Innovación pura sin boca a boca (q = 0)
    """
    p = max(p, 1e-8)
    return m * (1.0 - np.exp(-p * t))

def gompertz_model(t, m, k, t0):
    """
    Modelo de Gompertz - Difusión sigmoidea asimétrica
    """
    k = max(k, 1e-8)
    exponent = -k * (t - t0)
    exponent = np.clip(exponent, -700, 700)
    return m * np.exp(-np.exp(exponent))

def generalized_bass_model(t, m, p, q, beta):
    """
    Modelo de Bass Generalizado (Krishnan, Bass & Jain, 1994)
    Añade un multiplicador de shock temporal x(t) = 1 + beta * t
    """
    p = max(p, 1e-8)
    q = max(q, 0.0)
    
    t_arr = np.atleast_1d(t)
    t_max = int(np.ceil(np.max(t_arr)))
    t_grid = np.arange(t_max + 1)
    
    def f(time, N):
        if N >= m:
            return 0.0
        # Multiplicador de shock de marketing/precio
        x_t = 1.0 + beta * time
        x_t = max(x_t, 0.0)
        val = (p + (q / m) * N) * (m - N) * x_t
        return np.clip(val, 0.0, 1e6)
        
    N_grid = integrate_rk4(f, 0.0, t_grid)
    indices = np.clip(np.round(t_arr).astype(int), 0, t_max)
    res = N_grid[indices]
    return res[0] if np.isscalar(t) else res

def horsky_simon_model(t, m, p0, q, alpha):
    """
    Modelo de Horsky & Simon (1983) - Difusión con esfuerzo publicitario/marketing
    El coeficiente externo crece en el tiempo logarítmicamente: p(t) = p0 + alpha * ln(1 + t)
    """
    p0 = max(p0, 1e-8)
    q = max(q, 0.0)
    alpha = max(alpha, 0.0)
    
    t_arr = np.atleast_1d(t)
    t_max = int(np.ceil(np.max(t_arr)))
    t_grid = np.arange(t_max + 1)
    
    def f(time, N):
        if N >= m:
            return 0.0
        p_t = p0 + alpha * np.log(1.0 + time)
        val = (p_t + (q / m) * N) * (m - N)
        return np.clip(val, 0.0, 1e6)
        
    N_grid = integrate_rk4(f, 0.0, t_grid)
    indices = np.clip(np.round(t_arr).astype(int), 0, t_max)
    res = N_grid[indices]
    return res[0] if np.isscalar(t) else res

def muller_yogev_model(t, Ni, pi, qi, Nm, pm, qm, qim):
    """
    Modelo del Efecto Saddle de Muller & Yogev (2006)
    """
    pi = max(pi, 1e-8)
    qi = max(qi, 0.0)
    pm = max(pm, 1e-8)
    qm = max(qm, 0.0)
    qim = max(qim, 0.0)
    
    t_max = int(np.ceil(max(t)))
    t_grid = np.arange(t_max + 1)
    I_grid = bass_classic(t_grid, Ni, pi, qi)
    denom = max(Ni + Nm, 1e-8)
    
    def f(time, M):
        if M >= Nm:
            return 0.0
        I_val = bass_classic(time, Ni, pi, qi)
        val = (pm + qm * M / denom + qim * I_val / denom) * (Nm - M)
        val = np.clip(val, 0.0, 1e6)
        if not np.isfinite(val):
            return 0.0
        return val
        
    M_grid = integrate_rk4(f, 0.0, t_grid)
    total_grid = I_grid + M_grid
    
    indices = np.clip(np.round(t).astype(int), 0, t_max)
    return total_grid[indices]

def vdb_joshi_model(t, M1, p1, q1, M2, q2, w):
    """
    Modelo de Van den Bulte & Joshi (2007)
    """
    p1 = max(p1, 1e-8)
    q1 = max(q1, 0.0)
    q2 = max(q2, 0.0)
    w = np.clip(w, 0.0, 1.0)
    
    t_max = int(np.ceil(max(t)))
    t_grid = np.arange(t_max + 1)
    F1_grid = bass_classic(t_grid, 1.0, p1, q1)
    
    def f(time, F2):
        if F2 >= 1.0:
            return 0.0
        F1_val = bass_classic(time, 1.0, p1, q1)
        val = q2 * (w * F1_val + (1.0 - w) * F2) * (1.0 - F2)
        val = np.clip(val, 0.0, 1e6)
        if not np.isfinite(val):
            return 0.0
        return val
        
    F2_grid = integrate_rk4(f, 0.0, t_grid)
    total_grid = M1 * F1_grid + M2 * F2_grid
    
    indices = np.clip(np.round(t).astype(int), 0, t_max)
    return total_grid[indices]

def ladron_puts_model(t, S, alpha, beta, theta, gamma):
    """
    Modelo de Ladrón-de-Guevara & Putsis (2011) - Versión Uniproducto/Unimercado
    Con Mercado Potencial Dinámico y Endógeno:
    C(t) = 1.0 - theta * exp(-gamma * N(t) / S)
    M(t) = C(t) * S
    dN/dt = (alpha + beta * (N / M)) * (M - N)
    """
    S = max(S, 1e-5)
    alpha = max(alpha, 1e-8)
    beta = max(beta, 0.0)
    theta = np.clip(theta, 0.0, 1.0)
    gamma = max(gamma, 0.0)
    
    t_arr = np.atleast_1d(t)
    t_max = int(np.ceil(np.max(t_arr)))
    t_grid = np.arange(t_max + 1)
    
    def f(time, N):
        N = max(N, 0.0)
        frac = N / S
        frac = min(frac, 1.0)
        C = 1.0 - theta * np.exp(-gamma * frac)
        C = np.clip(C, 1e-8, 1.0)
        M = C * S
        if N >= M:
            return 0.0
        denom = max(M, 1e-5)
        dy_dt = (alpha + beta * (N / denom)) * (M - N)
        return max(dy_dt, 0.0)
        
    N_grid = integrate_rk4(f, 0.0, t_grid)
    indices = np.clip(np.round(t_arr).astype(int), 0, t_max)
    res = N_grid[indices]
    return res[0] if np.isscalar(t) else res
