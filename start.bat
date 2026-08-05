@echo off
echo =======================================
echo  FONPLATA - Iniciando aplicacion
echo =======================================
echo.

echo Iniciando backend (FastAPI)...
start "FONPLATA Backend" cmd /k "cd /d "%~dp0backend" && python -m uvicorn main:app --reload --port 8000"

echo Esperando que el backend arranque...
timeout /t 3 /nobreak > nul

echo Iniciando frontend (React)...
start "FONPLATA Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo.
echo =======================================
echo  App corriendo en: http://localhost:5173
echo  API docs en:      http://localhost:8000/docs
echo =======================================
echo.
echo Abriendo el navegador...
timeout /t 4 /nobreak > nul
start http://localhost:5173

pause
