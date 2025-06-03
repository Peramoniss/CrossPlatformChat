@echo off
set ROOT_DIR=%~dp0
cd /d "%ROOT_DIR%"
start "Server" cmd /k "python -m server.server"
start "Client 1" cmd /k "python -m client.client"
start "Client 2" cmd /k "python -m client.client"
