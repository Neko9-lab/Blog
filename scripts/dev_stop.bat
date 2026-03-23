@echo off
setlocal

echo Stopping processes on port 8000...
for /f "tokens=5" %%p in ('netstat -ano ^| findstr :8000') do (
  taskkill /F /PID %%p >nul 2>&1
)

echo Stopping processes on port 5173...
for /f "tokens=5" %%p in ('netstat -ano ^| findstr :5173') do (
  taskkill /F /PID %%p >nul 2>&1
)

echo Done.
endlocal
