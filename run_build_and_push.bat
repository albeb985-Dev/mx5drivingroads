@echo off
cd /d "%~dp0"

echo Generazione GeoJSON aggregati...
python-portable\python.exe scripts\build_geojson.py

echo.
echo Commit dei file aggiornati...
git add docs/*.geojson

git commit -m "Update aggregated GeoJSON" || echo Nessuna modifica da committare

echo.
echo Push verso GitHub...
git push

echo.
echo Tutto fatto.
pause
