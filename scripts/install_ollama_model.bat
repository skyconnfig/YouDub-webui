@echo off
chcp 65001 >nul
echo ============================================
echo Ollama 模型安装脚本（模型下载到当前目录）
echo ============================================
echo.

set OLLAMA_PATH=C:\Users\lixin\AppData\Local\Programs\Ollama
set MODEL=qwen2.5:7b

REM 获取项目根目录
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."
cd /d "%PROJECT_ROOT%"
set "PROJECT_ROOT=%CD%"
set "OLLAMA_MODELS=%PROJECT_ROOT%\models\ollama"

echo [信息] 项目目录: %PROJECT_ROOT%
echo [信息] 模型将下载到: %OLLAMA_MODELS%
echo.

echo [1/4] 检查 Ollama 路径...
if not exist "%OLLAMA_PATH%\ollama.exe" (
    echo [错误] 未找到 Ollama: %OLLAMA_PATH%\ollama.exe
    pause
    exit /b 1
)
echo [成功] 找到 Ollama

echo.
echo [2/4] 创建模型存储目录...
if not exist "%OLLAMA_MODELS%" (
    mkdir "%OLLAMA_MODELS%"
    echo [成功] 创建目录: %OLLAMA_MODELS%
) else (
    echo [信息] 目录已存在: %OLLAMA_MODELS%
)

echo.
echo [3/4] 启动 Ollama 服务...
tasklist /FI "IMAGENAME eq ollama.exe" 2>NUL | find /I /N "ollama.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo [信息] Ollama 服务已在运行
) else (
    echo [信息] 正在启动 Ollama 服务，模型存储: %OLLAMA_MODELS%
    start /B cmd /c "set OLLAMA_MODELS=%OLLAMA_MODELS% && "%OLLAMA_PATH%\ollama.exe" serve"
    timeout /t 5 /nobreak >nul
    echo [成功] Ollama 服务已启动
)

echo.
echo [4/4] 安装模型: %MODEL%
echo [提示] 模型大小约 4.4GB，下载位置: %OLLAMA_MODELS%
echo.
cd /d "%OLLAMA_PATH%"
set "OLLAMA_MODELS=%OLLAMA_MODELS%"
ollama.exe pull %MODEL%

if %errorlevel% == 0 (
    echo.
    echo ============================================
    echo [成功] 模型 %MODEL% 安装完成！
    echo ============================================
) else (
    echo.
    echo ============================================
    echo [错误] 模型安装失败
    echo ============================================
)

echo.
echo 已安装模型列表:
set "OLLAMA_MODELS=%OLLAMA_MODELS%"
"%OLLAMA_PATH%\ollama.exe" list
echo.
echo ============================================
echo 安装完成！
echo 模型存储位置: %OLLAMA_MODELS%
echo ============================================
echo.
pause
