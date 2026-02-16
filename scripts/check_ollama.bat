@echo off
chcp 65001 >nul
echo ============================================
echo Ollama 状态检查脚本
echo ============================================
echo.

set OLLAMA_PATH=C:\Users\lixin\AppData\Local\Programs\Ollama

echo [检查] Ollama 安装路径...
if exist "%OLLAMA_PATH%\ollama.exe" (
    echo [成功] 找到 Ollama: %OLLAMA_PATH%\ollama.exe
    
    echo.
    echo [检查] Ollama 版本...
    cd /d "%OLLAMA_PATH%"
    ollama.exe --version
    
    echo.
    echo [检查] Ollama 服务状态...
    tasklist /FI "IMAGENAME eq ollama.exe" | findstr "ollama.exe" >nul
    if %errorlevel% == 0 (
        echo [成功] Ollama 服务正在运行
    ) else (
        echo [警告] Ollama 服务未运行
        echo [提示] 正在启动服务...
        start /B "" "%OLLAMA_PATH%\ollama.exe" serve >nul 2>&1
        timeout /t 3 /nobreak >nul
        echo [成功] 服务已启动
    )
    
    echo.
    echo [检查] 已安装模型...
    ollama.exe list
    
    echo.
    echo [测试] 简单翻译测试...
    echo 正在进行翻译测试，请稍候...
    
    set "TEST_PROMPT=Translate the following to Chinese: 'Hello, how are you?'"
    
    echo {"model": "qwen2.5:7b", "prompt": "!TEST_PROMPT!", "stream": false} > %TEMP%\test.json
    
    curl -s -X POST http://localhost:11434/api/generate -H "Content-Type: application/json" -d @%TEMP%\test.json > %TEMP%\response.json 2>nul
    
    if exist %TEMP%\response.json (
        echo [成功] Ollama API 响应正常
        type %TEMP%\response.json | findstr "response" >nul
        if %errorlevel% == 0 (
            echo [成功] 翻译测试通过
        ) else (
            echo [警告] API 响应异常
        )
    ) else (
        echo [错误] 无法连接到 Ollama API
        echo [提示] 请检查 http://localhost:11434 是否可访问
    )
    
) else (
    echo [错误] 未找到 Ollama: %OLLAMA_PATH%\ollama.exe
    echo [提示] 请修改脚本中的 OLLAMA_PATH 变量
)

echo.
echo ============================================
echo 检查完成
echo ============================================
echo.
pause
