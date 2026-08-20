import os
import json
import sys
from report_validator import ModelFit, ReportValidator
from llm_reviewer import full_review

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

# Parse .env file if it exists to load api keys
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

# Also load from secrets.toml if available
secrets_path = os.path.join('.streamlit', 'secrets.toml')
if os.path.exists(secrets_path):
    import toml
    try:
        secrets = toml.load(secrets_path)
        if 'postgres' in secrets:
            for k, v in secrets['postgres'].items():
                os.environ[f"PG_{k.upper()}"] = str(v)
        if 'gemini' in secrets:
            key = secrets['gemini'].get('api_key') or secrets.get('gemini_api_key')
            if key:
                os.environ['GEMINI_API_KEY'] = key
    except Exception as e:
        print(f"Error loading secrets.toml: {e}")

# Clean up ANTHROPIC_API_KEY if it contains weird space characters
if 'ANTHROPIC_API_KEY' in os.environ:
    key = os.environ['ANTHROPIC_API_KEY']
    if 'R E V' in key:
        key = key.split('R E V')[0].strip()
    os.environ['ANTHROPIC_API_KEY'] = key

print(f"GEMINI_API_KEY present: {bool(os.environ.get('GEMINI_API_KEY'))}")
print(f"ANTHROPIC_API_KEY present: {bool(os.environ.get('ANTHROPIC_API_KEY'))}")

techs = ['spotify', 'chatgpt', 'claude', 'gemini']

for tech in techs:
    report_file = f"informe_global_{tech}.md"
    tables_file = f"informe_global_{tech}.md.tables.json"
    
    if not os.path.exists(report_file) or not os.path.exists(tables_file):
        print(f"Skipping {tech} (files not found)")
        continue
        
    print(f"\n==================================================")
    print(f"Running semantic review for {tech}...")
    print(f"==================================================")
    
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
        
    # Run Capa 1
    rv = ReportValidator(narrative_text, historical_table, model_fits, tolerance_pct=20.0)
    c1_issues = rv.run_all()
    print(f"--- Capa 1 (Determinista) detected {len(c1_issues)} issues:")
    for iss in c1_issues:
        print(f"  {iss}")
        
    # Run Capa 2 (Gemini)
    try:
        gemini_issues = full_review(narrative_text, historical_table, model_fits, backend='gemini', use_llm=True)
        c1_msg = {iss.message for iss in c1_issues}
        new_gemini_issues = [iss for iss in gemini_issues if iss.message not in c1_msg]
        print(f"--- Capa 2 (Gemini LLM) detected {len(new_gemini_issues)} NEW semantic issues:")
        for iss in new_gemini_issues:
            print(f"  {iss}")
    except Exception as e:
        print(f"  Error running Gemini reviewer: {e}")
        
    # Run Capa 2 (Claude)
    if False:  # os.environ.get('ANTHROPIC_API_KEY'):
        try:
            claude_issues = full_review(narrative_text, historical_table, model_fits, backend='claude', use_llm=True)
            c1_msg = {iss.message for iss in c1_issues}
            new_claude_issues = [iss for iss in claude_issues if iss.message not in c1_msg]
            print(f"--- Capa 2 (Claude LLM) detected {len(new_claude_issues)} NEW semantic issues:")
            for iss in new_claude_issues:
                print(f"  {iss}")
        except Exception as e:
            print(f"  Error running Claude reviewer: {e}")
