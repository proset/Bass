@echo off
title TechAdoption-Forecast (Bass)
cd /d "C:\Users\roset\Bass"
echo =====================================================================
echo Iniciando TechAdoption-Forecast (Bass) en el puerto 8503...
echo =====================================================================
echo.
python -m streamlit run app.py --server.port 8503
if %errorlevel% neq 0 (
    echo.
    echo Ocurrio un error al iniciar Streamlit. Asegurate de que Python esta instalado
    echo y que el puerto 8503 no este ocupado.
    pause
)
