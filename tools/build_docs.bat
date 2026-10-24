@echo off
setlocal DisableDelayedExpansion
set "DOCS_PYTHON=python"
if exist "%~dp0..\.venv\Scripts\python.exe" set "DOCS_PYTHON=%~dp0..\.venv\Scripts\python.exe"
if exist "%~dp0..\venv\Scripts\python.exe" set "DOCS_PYTHON=%~dp0..\venv\Scripts\python.exe"
"%DOCS_PYTHON%" "%~dp0build_docs.py"
exit /b %errorlevel%
