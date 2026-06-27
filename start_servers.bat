@echo off
cd /d D:\WOW\build\bin\RelWithDebInfo
echo Starting AzerothCore servers...
start "Authserver" authserver.exe
timeout /t 5 /nobreak >nul
start "Worldserver" worldserver.exe
echo Both servers started. Keep these windows open.
