import sys
import re
sys.path.append(r"C:\Users\roset\Bass")
from config import get_conn
import numpy as np
from models.rk4_solver import generalized_bass_model

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
    
    # anios_reales = [2021, 2022, 2023, 2024, 2025]
    # t_hist = [0, 1, 2, 3, 4]
    t_2031 = 2031 - 2021
    t_2036 = 2036 - 2021
    t_arr = np.array([t_2031, t_2036])
    v_arr = generalized_bass_model(t_arr, m, p, q, beta)
    v2031 = v_arr[0]
    v2036 = v_arr[1]
    
    inc1 = v2031 - 700.0
    inc2 = v2036 - v2031
    
    print("=== PROYECCIONES ESPERADAS GBM (Desde model_parameters) ===")
    print(f"v2031: {v2031:.2f} M")
    print(f"v2036: {v2036:.2f} M")
    print(f"Incremento 2025->2031 (v2031 - 700): {inc1:.2f} M")
    print(f"Incremento 2031->2036 (v2036 - v2031): {inc2:.2f} M")
    
    with open(r"C:\Users\roset\Bass\informe_global_chatgpt.md", "r", encoding="utf-8") as f:
        content = f.read()
    
    whitelist = ["0.0", "57.0", "180.5", "300.0", "700.0"]
    matches = re.finditer(r'(.{0,60})((?:\d{1,4}[.,])?\d+(?:[.,]\d+)?)\s*(?:M\b|millones)(.{0,60})', content, re.IGNORECASE)
    
    print("\n=== EXTRACCIÓN DEL INFORME ===")
    found = set()
    for m_obj in matches:
        left = m_obj.group(1).replace('\n', ' ')
        right = m_obj.group(3).replace('\n', ' ')
        val = m_obj.group(2)
        full_text = f"{left}[{val} M]{right}"
        
        ctx_lower = full_text.lower()
        if any(x in ctx_lower for x in ["2031", "2036", "incremento", "aument", "techo"]):
            if val not in whitelist:
                if full_text not in found:
                    found.add(full_text)
                    print(f"- {val} M => {full_text}")

if __name__ == '__main__':
    main()
