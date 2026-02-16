@echo off
chcp 65001 >nul
echo ============================================
echo YouDub + Ollama 启动脚本
echo ============================================
echo.

set OLLAMA_PATH=C:\Users\lixin\AppData\Local\Programs\Ollama

REM 获取项目目录
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."
cd /d "%PROJECT_ROOT%"
set "PROJECT_ROOT=%CD%"
set "OLLAMA_MODELS=%PROJECT_ROOT%\models\ollama"

echo [信息] 项目目录: %PROJECT_ROOT%
echo [信息] 模型目录: %OLLAMA_MODELS%
echo.

echo [1/3] 检查 Ollama...
if not exist "%OLLAMA_PATH%\ollama.exe" (
    echo [错误] 未找到 Ollama: %OLLAMA_PATH%\ollama.exe
    pause
    exit /b 1
)

REM 检查模型是否存在
if not exist "%OLLAMA_MODELS%\manifests" (
    echo [警告] 未找到模型文件！
    echo [提示] 请先运行: scripts\install_ollama_model.bat
    pause
    exit /b 1
)

echo [成功] Ollama 已找到，模型已安装

echo.
echo [2/3] 启动 Ollama 服务...
tasklist /FI "IMAGENAME eq ollama.exe" 2>NUL | find /I /N "ollama.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo [信息] Ollama 服务已在运行
) else (
    echo [信息] 正在启动 Ollama 服务...
    echo [信息] 模型位置: %OLLAMA_MODELS%
    
    REM 启动 Ollama 服务并设置环境变量
    start "Ollama Server" /B cmd /c "set OLLAMA_MODELS=%OLLAMA_MODELS% && cd /d %OLLAMA_PATH% && ollama.exe serve"
    
    echo [等待] 等待服务启动...
    timeout /t 5 /nobreak >nul
    
    REM 测试连接
    curl -s http://localhost:11434/api/tags >nul 2>&1
    if %errorlevel% == 0 (
        echo [成功] Ollama 服务已启动
    ) else (
        echo [警告] 服务可能未完全启动，继续尝试...
        timeout /t 3 /nobreak >nul
    )
)

echo.
echo [3/3] 启动 YouDub...
echo [信息] 使用翻译后端: Ollama (本地)
echo.

REM 激活虚拟环境并启动
call venv\Scripts\activate.bat

REM 设置环境变量并启动
set OLLAMA_MODELS=%OLLAMA_MODELS%
python app.py

echo.
echo [信息] YouDub 已关闭
echo.
pause
