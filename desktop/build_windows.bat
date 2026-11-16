@echo off
setlocal
cd /d "%~dp0"
echo Talaltam Windows alkalmazas - build
py -3 -m venv .venv
if errorlevel 1 goto error
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements-windows.txt
if errorlevel 1 goto error
pyinstaller --noconfirm --clean --windowed --onefile --name Talaltam --add-data "..\server;server" --collect-all webview --paths "..\server" --hidden-import app.main desktop_app.py
if errorlevel 1 goto error
echo.
echo Elkeszult: desktop\dist\Talaltam.exe
pause
exit /b 0
:error
echo Hiba tortent. Python 3.10-3.12 telepitese ajanlott.
pause
exit /b 1
