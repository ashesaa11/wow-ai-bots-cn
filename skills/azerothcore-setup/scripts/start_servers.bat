@echo off
cd /d "D:\WOW\build\bin\RelWithDebInfo"
start "AzerothCore Auth" authserver.exe
echo Waiting for authserver to initialize (15s)...
ping 127.0.0.1 -n 16 >nul
echo Starting worldserver...
start "AzerothCore World" cmd /c "worldserver.exe & echo. & echo Press any key to close... & pause >nul"
echo Done. Both servers should be running.
pause
