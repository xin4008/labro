@echo off
chcp 65001 >nul
cd /d "%~dp0"
title 化学实验助手

echo ========================================
echo   化学实验助手 - 分享模式（单窗口运行）
echo ========================================
echo.

where node >nul 2>&1
if errorlevel 1 (
  echo [错误] 未安装 Node.js，请先安装: https://nodejs.org/
  pause
  exit /b 1
)
where python >nul 2>&1
if errorlevel 1 (
  echo [错误] 未安装 Python，请先安装: https://www.python.org/
  pause
  exit /b 1
)

if not exist "backend\config.yaml" (
  echo [提示] 首次使用：正在从模板创建 config.yaml ...
  copy "backend\config.example.yaml" "backend\config.yaml"
  echo 请用记事本打开 backend\config.yaml 填写 DeepSeek API 密钥后重新运行。
  notepad "backend\config.yaml"
  pause
  exit /b 0
)

echo [1/3] 构建前端界面...
cd frontend
call npm install
call npm run build
if errorlevel 1 (
  echo 前端构建失败
  pause
  exit /b 1
)
cd ..

echo [2/3] 启动服务...
cd backend
if not exist ".venv" python -m venv .venv
call .venv\Scripts\activate.bat
pip install -q -r requirements.txt

echo.
echo [3/3] 请在浏览器打开:  http://127.0.0.1:8000
echo      同一 WiFi 下他人可访问: http://你的电脑IP:8000
echo      （需在 config.yaml 将 server.host 改为 0.0.0.0）
echo.
start http://127.0.0.1:8000
python run.py --prod

pause
