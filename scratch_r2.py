import sys
import os
sys.path.append(os.path.abspath("C:/Users/roset/Bass"))
from data.report_compiler import strip_numeric_prose
from difflib import ndiff

with open("scratch_r1.py", "r", encoding="utf-8") as f:
    exec(f.read())

import io
old_stdout = sys.stdout
sys.stdout = io.StringIO()

stripped = strip_numeric_prose("## 🤖 6. Informe Analítico Científico RAG\n" + new_block)
original = "## 🤖 6. Informe Analítico Científico RAG\n" + new_block

sys.stdout = old_stdout

print("DIFF FOR STRIP_NUMERIC_PROSE:")
for line in ndiff(original.splitlines(), stripped.splitlines()):
    if not line.startswith(' '):
        print(line)
