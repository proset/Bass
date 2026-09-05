"""
backtest_analogy.py — Backtest de 4 métodos para young-techs.
Métodos: A=persistencia, B=categoría(ritmo), C=forma(ritmo), D=GM(1,1).
"""
import json
import numpy as np
from scipy.optimize import curve_fit

K_ANALOGOS = 20  # top-K para el match por forma

# ---------- Curvas base ----------
def logistic_fixed_m(t, k, t0, m):
    # m is passed as extra arg or fixed in lambda
    return m / (1 + np.exp(-k * (np.array(t) - t0)))

# ---------- GM(1,1) de Deng ----------
def gm11_forecast(series, horizon):
    """
    Grey Model GM(1,1): proyección de tendencia con AGO.
    series: valores acumulados originales (n≥4).
    Retorna: lista de predicciones para los siguientes `horizon` pasos.
    """
    x0 = np.array(series, dtype=float)
    n = len(x0)
    if n < 4: return None
    
    # La serie ya es acumulada, el AGO estándar es cumsum (doble acumulación suaviza más)
    x1 = np.cumsum(x0)
    
    # Fondo gris (medias consecutivas)
    z1 = 0.5 * (x1[1:] + x1[:-1])  # longitud n-1
    
    # Resolver [a, u] por mínimos cuadrados: x0[k] = -a*z1[k] + u
    B = np.column_stack([-z1, np.ones(len(z1))])
    Y = x0[1:]
    try:
        a, u = np.linalg.lstsq(B, Y, rcond=None)[0]
    except Exception:
        return None
    if abs(a) < 1e-6: return None
    
    preds = []
    x1_0 = x1[0]
    c = x1_0 - u / a
    for t in range(n, n + horizon):
        x1_pred = c * np.exp(-a * t) + u / a
        x1_prev = c * np.exp(-a * (t - 1)) + u / a
        x0_pred = x1_pred - x1_prev
        preds.append(x0_pred)
    return preds

# ---------- El backtest ----------
def run_backtest():
    with open("data/catalog/curves.json", encoding="utf-8") as f:
        curves = json.load(f)
        
    by_ritmo = {}
    for c in curves:
        if c["ritmo"] == "Desconocido": continue
        by_ritmo.setdefault(c["ritmo"], []).append(c)
        
    results = {"A_persist": [], "B_cat": [], "C_forma": [], "D_gm11": []}
    results10 = {"A_persist": [], "B_cat": [], "C_forma": [], "D_gm11": []}
    fails = {"B_cat": 0, "C_forma": 0, "D_gm11": 0}
    cat_errors = {}
    
    n_eval = 0
    
    for ritmo, ritmo_curves in by_ritmo.items():
        if len(ritmo_curves) < 6: continue  # masa para leave-one-out
        
        for target in ritmo_curves:
            vals = np.array(target["values"])
            
            # Simular young-tech: 3 puntos desde el despegue (>1%)
            start = int(np.argmax(vals > 0.01))
            if vals[start] <= 0.01: continue # no despega
            
            t3 = start + 3
            if t3 + 10 >= len(vals): continue
            
            t_train = np.arange(3, dtype=float)
            y_train = vals[start:t3]
            y_true5 = vals[start + 5]
            y_true10 = vals[start + 10]
            
            # --- A. Persistencia ---
            errA5 = abs(y_train[-1] - y_true5) / max(y_true5, 0.01) * 100
            errA10 = abs(y_train[-1] - y_true10) / max(y_true10, 0.01) * 100
            
            # --- B. Prior de CATEGORÍA (en este rediseño es RITMO, leave-one-out) ---
            others_b = [c["values"][-1] for c in ritmo_curves if c["id"] != target["id"]]
            m_b = float(np.median(others_b))
            try:
                popt, _ = curve_fit(
                    lambda t, k, t0: logistic_fixed_m(t, k, t0, m_b),
                    t_train, y_train, p0=[0.5, 1.0], maxfev=5000)
                pred5B = logistic_fixed_m(5, *popt, m_b)
                pred10B = logistic_fixed_m(10, *popt, m_b)
                errB5 = abs(pred5B - y_true5) / max(y_true5, 0.01) * 100
                errB10 = abs(pred10B - y_true10) / max(y_true10, 0.01) * 100
            except Exception:
                errB5 = errB10 = None
                fails["B_cat"] += 1
                
            # --- C. Prior por FORMA (leave-one-out, dentro del mismo RITMO) ---
            def norm_start(v):
                techo = v[-1]
                if techo == 0: return [], 1.0
                s = int(np.argmax(np.array(v) > 0.01))
                if s + 3 > len(v): return [], 1.0
                return np.array(v[s:s+3]) / techo, techo
                
            y_norm, _ = norm_start(target["values"])
            dists = []
            for c in ritmo_curves:
                if c["id"] == target["id"]: continue
                cn, techo_c = norm_start(c["values"])
                if len(cn) < 3: continue
                d = np.linalg.norm(cn - y_norm)
                dists.append((d, techo_c))
            dists.sort(key=lambda x: x[0])
            topk = [t for _, t in dists[:K_ANALOGOS]]
            
            m_c = float(np.median(topk)) if topk else m_b
            try:
                popt, _ = curve_fit(
                    lambda t, k, t0: logistic_fixed_m(t, k, t0, m_c),
                    t_train, y_train, p0=[0.5, 1.0], maxfev=5000)
                pred5C = logistic_fixed_m(5, *popt, m_c)
                pred10C = logistic_fixed_m(10, *popt, m_c)
                errC5 = abs(pred5C - y_true5) / max(y_true5, 0.01) * 100
                errC10 = abs(pred10C - y_true10) / max(y_true10, 0.01) * 100
            except Exception:
                errC5 = errC10 = None
                fails["C_forma"] += 1
                
            # --- D. GM(1,1) ---
            # gm11 needs at least 4 points according to our current implementation (we send 3 points y_train). 
            # Wait, the user prompt said: t_train = np.arange(3), y_train = vals[start:t3]. That's 3 points!
            # If GM(1,1) requires n>=4, I must change GM11 to accept n=3 or send 4 points. The prompt says "con 3-4 puntos", but explicitly writes y_train=vals[start:t3] which is 3 points. Let's fix GM11 to accept n=3.
            gm_series = y_train
            if len(gm_series) < 3:
                gm5 = gm10 = None
                fails["D_gm11"] += 1
            else:
                x0 = np.array(gm_series, dtype=float)
                n = len(x0)
                x1 = np.cumsum(x0)
                z1 = 0.5 * (x1[1:] + x1[:-1])
                B = np.column_stack([-z1, np.ones(len(z1))])
                Y = x0[1:]
                try:
                    a, u = np.linalg.lstsq(B, Y, rcond=None)[0]
                    if abs(a) < 1e-6:
                        gm5 = gm10 = None
                        fails["D_gm11"] += 1
                    else:
                        c_val = x1[0] - u / a
                        gm5_val = None
                        gm10_val = None
                        
                        # Calculate for t=3,4,5,... (indexes relative to start)
                        # We want the values at start+5 and start+10. 
                        # n=3. The next steps are t=3,4,5...
                        for t in range(n, n + 8):
                            x1_pred = c_val * np.exp(-a * t) + u / a
                            x1_prev = c_val * np.exp(-a * (t - 1)) + u / a
                            x0_pred = x1_pred - x1_prev
                            if t == 5: gm5_val = x0_pred
                            if t == 10: gm10_val = x0_pred
                            
                        if gm5_val is not None:
                            errD5 = abs(gm5_val - y_true5) / max(y_true5, 0.01) * 100
                        else:
                            errD5 = None
                            
                        if gm10_val is not None:
                            errD10 = abs(gm10_val - y_true10) / max(y_true10, 0.01) * 100
                        else:
                            errD10 = None
                except Exception:
                    errD5 = errD10 = None
                    fails["D_gm11"] += 1

            # Acumular
            results["A_persist"].append(errA5)
            results10["A_persist"].append(errA10)
            
            for key, e5, e10 in [("B_cat", errB5, errB10),
                                 ("C_forma", errC5, errC10),
                                 ("D_gm11", errD5, errD10)]:
                if e5 is not None:
                    results[key].append(e5)
                if e10 is not None:
                    results10[key].append(e10)
                    
            if errC5 is not None and errC10 is not None:
                target_cat = target["categoria"]
                if target_cat not in cat_errors:
                    cat_errors[target_cat] = {"e5": [], "e10": []}
                cat_errors[target_cat]["e5"].append(errC5)
                cat_errors[target_cat]["e10"].append(errC10)
                
            n_eval += 1

    # ---------- Reporte ----------
    print("=" * 70)
    print(f"BACKTEST 4 MÉTODOS — {n_eval} curvas evaluadas (leave-one-out)")
    print("=" * 70)
    print(f"{'Método':15s} {'MAPE 5y (mediana)':>20s} {'MAPE 10y (mediana)':>20s} {'Fallos':>10s}")
    for key in ["A_persist", "B_cat", "C_forma", "D_gm11"]:
        m5 = np.median(results[key]) if results[key] else float('nan')
        m10 = np.median(results10[key]) if results10[key] else float('nan')
        f = fails.get(key, 0)
        print(f"{key:15s} {m5:19.1f}% {m10:19.1f}% {f:10d}")
    print("=" * 70)
    
    print("\nDesglose del método C (forma) por categoría:")
    for cat, errs in cat_errors.items():
        m5 = np.median(errs["e5"])
        m10 = np.median(errs["e10"])
        print(f"  {cat:15s}: MAPE 5y={m5:5.1f}% | MAPE 10y={m10:5.1f}% (N={len(errs['e5'])})")
        
    print("\nCRITERIOS DE LECTURA:")
    print("C > B > A -> el match por forma aporta valor real")
    print("C vs D a 10y -> la analogía gana donde GM no puede ir (techo)")
    print("C ≈ D a 5y -> la analogía solo aporta a largo plazo")

if __name__ == "__main__":
    run_backtest()
