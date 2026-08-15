@echo off
rem Autostart for local AI stack (Ollama LLM + Voicebox TTS) at Windows login.
rem Register: HKCU\Software\Microsoft\Windows\CurrentVersion\Run  "AIStack" = "C:\Users\<user>\start-ai-stack.bat"
rem (powershell: Set-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run' -Name 'AIStack' -Value '<path>')

rem --- Ollama (if not running) ---
tasklist /fi "imagename eq ollama.exe" 2>nul | find /i "ollama.exe" >nul
if errorlevel 1 (
    start "" "C:\Users\<user>\AppData\Local\Programs\Ollama\ollama.exe" serve
)

rem --- Voicebox TTS (if not running) ---
curl -s --max-time 2 http://127.0.0.1:8000/health >nul 2>&1
if errorlevel 1 (
    start "" "C:\Users\<user>\Voicebox\voicebox-server.exe"
)

rem --- Wait for Voicebox to come up ---
timeout /t 3 /nobreak >nul
