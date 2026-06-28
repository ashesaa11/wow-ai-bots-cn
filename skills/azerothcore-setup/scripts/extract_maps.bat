@echo off
cd /d "D:\WOW\World of Warcraft 3.3.5a CN"
echo Extracting maps and DBC...
map_extractor.exe -i "D:\WOW\World of Warcraft 3.3.5a CN" -o "D:\WOW\build\bin\RelWithDebInfo"
echo.
echo Done. Press any key to close.
pause >nul
