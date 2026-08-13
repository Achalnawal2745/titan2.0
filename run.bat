@echo off
set OPENBLAS_NUM_THREADS=1
set MKL_NUM_THREADS=1
set NUMEXPR_NUM_THREADS=1
set OMP_NUM_THREADS=1

echo ======================================================
echo           STARTING TITAN NEURAL ENGINE
echo ======================================================

.\venv\Scripts\python.exe main.py
if errorlevel 1 (
    echo.
    echo Press any key to exit...
    pause > nul
)
