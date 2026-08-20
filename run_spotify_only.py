import os
import json
import sys
from report_validator import ModelFit, ReportValidator
from llm_reviewer import full_review

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

# load keys
if os.path.exists('.env'):
    with open('.env', 'rb') as f:
        content = f.read().replace(b'\x00', b'')
        try:
            text = content.decode('utf-8')
        except UnicodeDecodeError:
            text = content.decode('utf-16', errors='ignore')
        for line in text.splitlines():
            if '=' in line:
                name, val = line.strip().split('=', 1)
                os.environ[name.strip()] = val.strip()

secrets_path = os.path.join('.streamlit', 'secrets.toml')
if os.path.exists(secrets_path):
    import toml
    try:
        secrets = toml.load(secrets_path)
        if 'gemini' in secrets:
            key = secrets['gemini'].get('api_key') or secrets.get('gemini_api_key')
            if key:
                os.environ['GEMINI_API_KEY'] = key
    except Exception as e:
        print(f"Error loading secrets.toml: {e}")

print("Loading files for spotify...")
report_file = "informe_global_spotify.md"
tables_file = "informe_global_spotify.md.tables.json"

with open(report_file, 'r', encoding='utf-8') as f:
    narrative_text = f.read()
    
with open(tables_file, 'r', encoding='utf-8') as f:
    data = json.load(f)
    historical_table = {int(k): v for k, v in data.get("historical", {}).items()}
    model_fits = [
        ModelFit(m["name"], m["r2"], m["mape"],
                 {int(k): v for k, v in m.get("projections", {}).items()})
        for m in data.get("models", [])
    ]

print("Running Capa 1...")
rv = ReportValidator(narrative_text, historical_table, model_fits, tolerance_pct=20.0)
c1_issues = rv.run_all()
print(f"Capa 1 issues: {len(c1_issues)}")
for iss in c1_issues:
    print(f"  {iss}")

print("Running Capa 2 (Gemini)...")
try:
    gemini_issues = full_review(narrative_text, historical_table, model_fits, backend='gemini', use_llm=True)
    c1_msg = {iss.message for iss in c1_issues}
    new_gemini_issues = [iss for iss in gemini_issues if iss.message not in c1_msg]
    print(f"Capa 2 issues: {len(new_gemini_issues)}")
    for iss in new_gemini_issues:
        print(f"  {iss}")
except Exception as e:
    print("Gemini failed:", e)
