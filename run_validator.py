import sys
import os
import json
sys.path.append(r"C:\Users\roset\Bass")
from report_validator import ReportValidator, ModelFit

def validate_existing():
    file_name = "informe_global_chatgpt.md"
    tables_path = file_name + ".tables.json"
    
    with open(file_name, "r", encoding="utf-8") as f:
        report_text = f.read()
        
    historical_table = {}
    model_fits = []
    
    if os.path.exists(tables_path):
        with open(tables_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            historical_table = {int(k): v for k, v in data.get("historical", {}).items()}
            model_fits = [
                ModelFit(m["name"], m["r2"], m["mape"],
                         {int(k): v for k, v in m.get("projections", {}).items()})
                for m in data.get("models", [])
            ]
            
    validator = ReportValidator(report_text, historical_table, model_fits, tolerance_pct=20.0)
    issues = validator.run_all()
    
    for i in issues:
        print(i.severity, i.category, i.message)
        if i.evidence:
            print("  ->", i.evidence)

if __name__ == "__main__":
    validate_existing()
