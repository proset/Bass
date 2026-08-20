import sys
import os
import traceback
sys.path.append(r"C:\Users\roset\Bass")
from data.report_compiler import compilar_informe_global
import logging

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    try:
        print("Compiling ChatGPT report...")
        compilar_informe_global("chatgpt")
        print("SUCCESS!")
    except Exception as e:
        print("FAILED!")
        traceback.print_exc()
