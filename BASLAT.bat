@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\pythonw.exe" (
    echo [INFO] Sanal ortam bulunamadi. Ilk kurulum baslatiliyor...
    call "%~dp0kurulum.bat"
    if not %errorlevel%==0 (
        echo [HATA] Kurulum basarisiz. Program baslatilamadi.
        pause
        exit /b 1
    )
)

call ".venv\Scripts\activate.bat"

REM Ollama calisiyorsa High priority'ye al
powershell -NoProfile -Command "Get-Process ollama -ErrorAction SilentlyContinue | ForEach-Object { $_.PriorityClass = 'High' }"

REM Uygulamayi High priority ile baslat
start "AI Asistan" /B /HIGH ".venv\Scripts\pythonw.exe" "%~dp0main.pyw"
exit /b 0
