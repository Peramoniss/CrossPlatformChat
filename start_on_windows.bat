@echo off

start "Server" cmd /k "python server.py"
start "Client 1" cmd /k "python client.py"
start "Client 2" cmd /k "python client.py"
