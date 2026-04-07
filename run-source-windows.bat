@echo off
REM glmfix -- run from source on Windows
set SCRIPT_DIR=%~dp0
python "%SCRIPT_DIR%glmfix.py" %*
