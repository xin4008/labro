@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo   化学实验助手 - 正在启动...
echo ========================================

if not exist "data" mkdir "data"

pip install -r requirements.txt -q
python app.py
pause
