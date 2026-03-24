@echo off
setlocal

cd /d %~dp0\..

echo [1/3] Create venv if missing
if not exist .venv (
  py -3.11 -m venv .venv
)

echo [2/3] Install backend deps
.venv\Scripts\pip install -r requirements.txt

cd /d %~dp0\..\backend

if not exist alembic.ini (
  echo alembic.ini not found
  exit /b 1
)

..\.venv\Scripts\alembic upgrade head
if errorlevel 1 exit /b 1

..\.venv\Scripts\python -m scripts.seed
if errorlevel 1 exit /b 1

echo Starting backend...
start "backend" cmd /k "cd /d %~dp0\..\backend && ..\.venv\Scripts\python -m uvicorn main:app --reload --port 8000"

cd /d %~dp0\..\frontend
echo Installing frontend deps...
call npm install
if errorlevel 1 exit /b 1

echo Starting frontend...
start "frontend" cmd /k "cd /d %~dp0\..\frontend && npm run dev -- --host"

echo Done. Open http://localhost:5173/
endlocal
