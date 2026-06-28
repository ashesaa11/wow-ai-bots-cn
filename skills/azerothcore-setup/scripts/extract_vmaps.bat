@echo off
cd /d "D:\WOW\World of Warcraft 3.3.5a CN"
echo === Step 1/2: Extracting vmap data ===
vmap4_extractor.exe -d "D:\WOW\World of Warcraft 3.3.5a CN\Data"
echo.
echo === Step 2/2: Assembling vmaps ===
mkdir "D:\WOW\build\bin\RelWithDebInfo\vmaps" 2>nul
vmap4_assembler.exe Buildings "D:\WOW\build\bin\RelWithDebInfo\vmaps"
echo.
echo Done. Press any key to close.
pause >nul
