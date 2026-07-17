@echo off
:: ─────────────────────────────────────────────────────────────────────────────
:: Krishi Market Advisor — Unattended Automation Script
::
:: This batch file is designed to be executed by Windows Task Scheduler.
:: It automatically changes the directory to the project folder, activates the
:: Python virtual environment (if present), runs the pipeline, and logs any
:: output to logs/scheduler.log.
:: ─────────────────────────────────────────────────────────────────────────────

:: Change the working directory to the directory where this batch file is located
cd /d "%~dp0"

:: Set up logs directory if not already created
if not exist logs mkdir logs

:: Record execution start time in the scheduler log
echo =================================──────── >> logs\scheduler.log
echo Execution started at: %date% %time% >> logs\scheduler.log

:: Activate the Python virtual environment if it exists in the project root
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment... >> logs\scheduler.log
    call venv\Scripts\activate.bat
) else (
    echo No virtual environment found. Using system Python... >> logs\scheduler.log
)

:: Run the main data collection pipeline, forwarding all outputs to logs/scheduler.log
python main.py >> logs\scheduler.log 2>&1

:: Record termination status
echo Execution finished with code %errorlevel% at: %date% %time% >> logs\scheduler.log
echo =================================──────── >> logs\scheduler.log
