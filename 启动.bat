@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo   Labro - 启动（React + FastAPI）
echo ========================================
echo.
echo 将打开两个窗口：后端 API (8000) + 前端页面 (5173)
echo 请在浏览器访问: http://localhost:5173
echo 不要只打开 http://127.0.0.1:8000 （那是 API，不是界面）
echo.

start "Labro-后端" cmd /k "cd /d "%~dp0backend" && (if not exist .venv python -m venv .venv) && .venv\Scripts\activate.bat && pip install -q -r requirements.txt && python run.py"

timeout /t 3 /nobreak >nul

start "Labro-前端" cmd /k "cd /d "%~dp0frontend" && npm install && npm run dev"

timeout /t 5 /nobreak >nul
start http://localhost:5173

echo.
echo 已尝试打开浏览器。若页面空白，请确认「前端」窗口无报错。
pause
