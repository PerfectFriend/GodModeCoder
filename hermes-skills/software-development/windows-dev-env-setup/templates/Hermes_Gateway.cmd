@echo off
rem =============================================================================
rem Hermes Gateway Launcher - <BOT-NAME>
rem Copy to gateways/<bot-name>/Hermes_Gateway.cmd and update paths
rem =============================================================================

cd /d C:\Users\<user>\AppData\Local\hermes

set "HERMES_HOME=C:\Users\<user>\AppData\Local\hermes"
set "DOTENV_PATH=C:\Users\<user>\AppData\Local\hermes\gateways\<bot-name>\.env"

set "PYTHONIOENCODING=utf-8"
set "HERMES_GATEWAY_DETACHED=1"
set "VIRTUAL_ENV=C:\Users\<user>\AppData\Local\hermes\hermes-agent\venv"
set "PYTHONPATH=C:\Users\<user>\AppData\Local\hermes\hermes-agent;%PYTHONPATH%"

C:\Users\<user>\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe -m hermes_cli.main gateway run

exit /b 0