import numpy as np
from data.loaders import load_historical_data, load_model_parameters
from models.rk4_solver import dual_market_bass, generalized_bass_model, bass_classic

tech = 'claude'
df = load_historical_data(tech)
params = load_model_parameters(tech)

print("=== SERIE HISTORICA ACTUAL EN BD ===")
print(df[['anio', 'adopcion_acumulada']].to_string(index=False))

t_hist_len = len(df)
ultimo_anio = int(df['anio'].max())

print(f"\n=== PROYECCIONES 2026-2035 (base: {ultimo_anio}, t={t_hist_len}) ===")
print(f"{'Modelo':35s} {'2026':>8} {'2028':>8} {'2030':>8} {'2035':>8}")
print("-" * 65)

for modelo, p in sorted(params.items(), key=lambda x: -x[1].get('r_cuadrado', 0)):
    r2 = p.get('r_cuadrado', 0)
    try:
        vals = []
        for yr in [2026, 2028, 2030, 2035]:
            t = t_hist_len + (yr - ultimo_anio)
            if modelo == 'Dual_Market':
                v = dual_market_bass(t, p['param_m1'], p['param_p1'], p['param_q1'], p['param_m2'], p['param_p2'], p['param_q2'])
            elif modelo == 'Generalized_Bass':
                v = generalized_bass_model(np.array([t]), p['param_m1'], p['param_p1'], p['param_q1'], p['param_p2'])[0]
            elif modelo == 'Bass_Clasico':
                v = bass_classic(t, p['param_m1'], p['param_p1'], p['param_q1'])
            else:
                vals = None
                break
            vals.append(v)
        if vals:
            print(f"{modelo:35s} {vals[0]:>8.1f} {vals[1]:>8.1f} {vals[2]:>8.1f} {vals[3]:>8.1f}  (R²={r2:.4f})")
    except Exception as e:
        print(f"{modelo:35s} ERROR: {e}")
