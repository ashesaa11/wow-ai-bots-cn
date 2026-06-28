@echo off
cd /d "D:\WOW\build\bin\RelWithDebInfo"
echo Generating mmaps - this may take 30-60 minutes...
echo.
mmaps_generator.exe
echo.
echo Done! All map data extracted.
pause
