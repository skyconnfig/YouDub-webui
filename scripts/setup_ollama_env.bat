@echo off
chcp 65001 >nul
echo ============================================
echo Ollama 环境变量设置工具（模型存到项目目录）
echo ============================================
echo.

set OLLAMA_PATH=C:\Users\lixin\AppData\Local\Programs\Ollama

REM 获取项目目录
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."
cd /d "%PROJECT_ROOT%"
set "PROJECT_ROOT=%CD%"
set "OLLAMA_MODELS_DIR=%PROJECT_ROOT%\models\ollama"

if not exist "%OLLAMA_PATH%\ollama.exe" (
    echo [错误] 未找到 Ollama: %OLLAMA_PATH%
    pause
    exit /b 1
)

echo [信息] Ollama: %OLLAMA_PATH%
echo [信息] 模型将存储到: %OLLAMA_MODELS_DIR%
echo.

echo [1/3] 添加 Ollama 到 PATH...
setx PATH "%PATH%;%OLLAMA_PATH%" >nul 2>&1
if %errorlevel% == 0 (
    echo [成功] Ollama 已添加到 PATH
) else (
    echo [警告] 添加到 PATH 失败，请手动添加
)

echo.
echo [2/3] 创建模型存储目录...
if not exist "%OLLAMA_MODELS_DIR%" (
    mkdir "%OLLAMA_MODELS_DIR%"
    echo [成功] 创建目录: %OLLAMA_MODELS_DIR%
) else (
    echo [信息] 目录已存在: %OLLAMA_MODELS_DIR%
)

echo.
echo [3/3] 设置 OLLAMA_MODELS 环境变量...
setx OLLAMA_MODELS "%OLLAMA_MODELS_DIR%" >nul 2>&1
echo [成功] OLLAMA_MODELS = %OLLAMA_MODELS_DIR%

echo.
echo ============================================
echo 环境变量设置完成！
echo ============================================
echo.
echo 请关闭并重新打开命令提示符
echo 然后运行: install_ollama_model.bat
echo.
pause
