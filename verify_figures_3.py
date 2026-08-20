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
    
    t_2031 = 2031 - 2021 + 1
    t_2036 = 2036 - 2021 + 1
    t_arr = np.array([t_2031, t_2036])
    v_arr = generalized_bass_model(t_arr, m, p, q, beta)
    v2031 = v_arr[0]
    v2036 = v_arr[1]
    
    inc1 = v2031 - 700.0
    inc2 = v2036 - v2031
    
    print("=== EXPECTED ===")
    print(f"2031: {v2031:.2f}")
    print(f"2036: {v2036:.2f}")
    print(f"inc 2025->2031: {inc1:.2f}")
    print(f"inc 2031->2036: {inc2:.2f}")

if __name__ == '__main__':
    main()
