@echo off
REM Windows launcher.  Usage:  run.bat experiment [quick]   or   run.bat base [NAME]   (profiles: experiment | smoke | tiny | base)
setlocal
cd /d "%~dp0"
set PYTHONUTF8=1
if not defined CKPT_DIR if exist D:\ set "CKPT_DIR=D:\model_checkpoints\ner_enrich_pkg"
set TOKENIZERS_PARALLELISM=false
set HF_HUB_DISABLE_SYMLINKS_WARNING=1
set PROFILE=%1
if "%PROFILE%"=="" set PROFILE=smoke
set NAME=%2
if "%NAME%"=="" set NAME=%PROFILE%

REM Use the project venv's Python if present, else fall back to python on PATH
set PY=python
if exist "%~dp0..\venv\Scripts\python.exe" set PY=%~dp0..\venv\Scripts\python.exe
if exist "%~dp0venv\Scripts\python.exe"    set PY=%~dp0venv\Scripts\python.exe
"%PY%" --version

where nvidia-smi >nul 2>nul
if %errorlevel%==0 (
  "%PY%" -c "import torch,sys; sys.exit(0 if torch.cuda.is_available() else 1)" >nul 2>nul
  if errorlevel 1 (
    echo NVIDIA GPU detected, installing CUDA torch...
    "%PY%" -m pip install -q --force-reinstall torch --index-url https://download.pytorch.org/whl/cu124
  )
) else (
  "%PY%" -m pip install -q torch
)
"%PY%" -m pip install -q -r "%~dp0requirements.txt"
"%PY%" -c "import torch; print('torch', torch.__version__, '| cuda:', torch.cuda.is_available())"

if "%PROFILE%"=="experiment" (
  if "%2"=="quick" ( "%PY%" experiment.py --quick ) else ( "%PY%" experiment.py )
  goto :eof
)
if "%PROFILE%"=="smoke" "%PY%" sweep.py --name %NAME% --alphas 1.0 --seeds 0 --n_replicate 2 --n_base 1500 --epochs_base 1 --n_pass 500 --n_eval 600
if "%PROFILE%"=="tiny"  "%PY%" sweep.py --name %NAME% --alphas 0.5 1.0 2.0 --seeds 0 1 2 --n_replicate 2 --n_base 6000 --epochs_base 2 --n_pass 1500 --n_eval 1500
if "%PROFILE%"=="base"  "%PY%" sweep.py --name %NAME% --model bert-base-uncased --alphas 0.25 0.5 1.0 2.0 --seeds 0 1 2 --n_replicate 3 --n_base 10000 --epochs_base 2 --n_pass 2500 --n_eval 2500 --lr 3e-5 --kl_beta 0.2
echo.
echo Results: see the "result package" line above (runs/ keeps the full ledgers and checkpoints).
endlocal
