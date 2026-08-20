import sys
import re
sys.path.append(r"C:\Users\roset\Bass")
from config import get_conn
import numpy as np

# from models.rk4_solver
def generalized_bass_model(t, m, p, q, beta):
    from scipy.integrate import odeint
    def deriv(N, t_val, m_val, p_val, q_val, beta_val):
        return (p_val + q_val * (N / m_val)) * (m_val - N) * (t_val ** beta_val)
    if isinstance(t, (int, float)):
        t_arr = np.linspace(0, t, max(2, int(t)*10))
    else:
        t_arr = np.concatenate(([0], t))
    N0 = 0
    sol = odeint(deriv, N0, t_arr, args=(m, p, q, beta))
    if isinstance(t, (int, float)):
        return sol[-1][0]
    return sol[1:, 0]

def main():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT param_p1, param_q1, param_m1, param_p2 FROM model_parameters WHERE tecnologia='chatgpt' AND modelo_tipo='Generalized_Bass'")
    row = c.fetchone()
    conn.close()
    
    if not row:
        print("No parameters found")
        return
    p, q, m, beta = row
    
    t_2031 = 2031 - 2021 + 1
    t_2036 = 2036 - 2021 + 1
    t_arr = np.array([t_2031, t_2036])
    v_arr = generalized_bass_model(t_arr, m, p, q, beta)
    v2031 = v_arr[0]
    v2036 = v_arr[1]
    
    inc1 = v2031 - 700.0
    inc2 = v2036 - v2031
    
    print("=== CÁLCULO DE PROYECCIONES GBM (Desde parámetros DB) ===")
    print(f"v2031: {v2031:.2f} M")
    print(f"v2036 (Techo): {v2036:.2f} M")
    print(f"Incremento 2025->2031: {inc1:.2f} M")
    print(f"Incremento 2031->2036: {inc2:.2f} M")
    print("\n=== CIFRAS DEL INFORME (Con contexto) ===")
    
    with open(r"C:\Users\roset\Bass\informe_global_chatgpt.md", "r", encoding="utf-8") as f:
        content = f.read()
    
    whitelist = ["0.0", "57.0", "180.5", "300.0", "700.0"]
    matches = re.finditer(r'(.{0,50})(\b\d+(?:\.\d+)?\b)\s*(?:M\b|millones)(.{0,50})', content, re.IGNORECASE)
    
    found = set()
    for m_obj in matches:
        left = m_obj.group(1).replace('\n', ' ')
        right = m_obj.group(3).replace('\n', ' ')
        val = m_obj.group(2)
        full_text = f"{left}[{val} M]{right}"
        
        ctx_lower = full_text.lower()
        if any(x in ctx_lower for x in ["2031", "2036", "incremento", "aument", "techo"]):
            if val not in whitelist:
                # To avoid duplicates in printing
                if full_text not in found:
                    found.add(full_text)
                    print(f"- {val} M => {full_text}")

if __name__ == '__main__':
    main()
