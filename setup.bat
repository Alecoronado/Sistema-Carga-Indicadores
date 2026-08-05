@echo off
echo =======================================
echo  FONPLATA - Setup inicial
echo =======================================
echo.

echo [1/3] Instalando dependencias del backend...
cd /d "%~dp0backend"
pip install -r requirements.txt
if errorlevel 1 (echo ERROR en pip install & pause & exit /b 1)

echo.
echo [2/3] Instalando dependencias del frontend...
cd /d "%~dp0frontend"
npm install
if errorlevel 1 (echo ERROR en npm install & pause & exit /b 1)

echo.
echo [3/3] Importando datos del Excel a la base de datos...
cd /d "%~dp0backend"
python import_excel.py
if errorlevel 1 (echo ERROR en importacion & pause & exit /b 1)

echo.
echo =======================================
echo  Setup completado exitosamente!
echo  Ejecuta start.bat para iniciar la app.
echo =======================================
pause
