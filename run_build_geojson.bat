@echo off
cd /d "%~dp0"

echo Generazione GeoJSON aggregati...
python-portable\pythonportable.exe scripts\build_geojson.py

echo.
echo Operazione completata.
pause
