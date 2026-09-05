import json
from config import get_conn

def check_db():
    conn = get_conn()
    cur = conn.cursor()
    
    # We use LOWER(TRIM(tecnologia)) as inserted. The table column is 'tecnologia', not 'tech'
    cur.execute("SELECT tecnologia, modelo_tipo, param_m1, r_cuadrado, score FROM model_parameters WHERE tecnologia = 'chatgpt'")
    print('MODEL PARAMS:')
    for row in cur.fetchall():
        print(row)
        
    cur.execute("SELECT analisis FROM qualitative_analysis WHERE tecnologia = 'chatgpt'")
    print('\nQUALITATIVE (scenarios summary):')
    res = cur.fetchone()
    if res:
        print(json.dumps(json.loads(res[0]), indent=2)[:500] + '...')
    else:
        print('None')
        
    cur.close()
    conn.close()

if __name__ == "__main__":
    check_db()
