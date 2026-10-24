@echo off
setlocal DisableDelayedExpansion

if "%~1"=="" goto usage
if not "%2"=="" goto usage

set "TEST_API="
if /i "%~1"=="all" goto run
if /i "%~1"=="openai" set "TEST_API=OpenAI"
if /i "%~1"=="claude" set "TEST_API=Claude"
if /i "%~1"=="gemini" set "TEST_API=Gemini"
if /i "%~1"=="azureopenai" set "TEST_API=AzureOpenAI"
if not defined TEST_API goto usage

:run
set "TEST_PYTHON=python"
if exist "%~dp0..\.venv\Scripts\python.exe" set "TEST_PYTHON=%~dp0..\.venv\Scripts\python.exe"
if exist "%~dp0..\venv\Scripts\python.exe" set "TEST_PYTHON=%~dp0..\venv\Scripts\python.exe"

if defined TEST_API goto service
"%TEST_PYTHON%" "%~dp0test_agent_live.py" --run-live-api --all-models
exit /b %errorlevel%

:service
"%TEST_PYTHON%" "%~dp0test_agent_live.py" --run-live-api --api %TEST_API% --all-models
exit /b %errorlevel%

:usage
echo Usage: %~nx0 all ^| openai ^| claude ^| gemini ^| azureopenai
echo Specify exactly one argument. Real API calls incur charges.
exit /b 2
