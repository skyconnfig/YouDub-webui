@echo off
chcp 65001 >nul
cls
echo ============================================
echo  YouDub-webui - 视频翻译配音工具
echo ============================================
echo.

:: Check for Deno
set "DENO_PATH="
set "DENO_DIR=%USERPROFILE%\.deno\bin"

IF EXIST "%DENO_DIR%\deno.exe" (
    echo [1/4] ✅ Found Deno
    set "DENO_PATH=%DENO_DIR%\deno.exe"
) ELSE (
    echo [1/4] ⚠️  Deno not found. Attempting to install...
    echo.
    powershell -Command "irm https://deno.land/install.ps1 | iex"
    
    IF EXIST "%DENO_DIR%\deno.exe" (
        echo ✅ Deno installed successfully
        set "DENO_PATH=%DENO_DIR%\deno.exe"
    ) ELSE (
        echo ❌ Deno installation failed
        echo Please install manually: https://deno.land/
        pause
        exit /b 1
    )
)

:: Add Deno to PATH for this session
echo [2/4] Configuring environment...
set "PATH=%DENO_DIR%;%PATH%"
set "DENO_INSTALL=%USERPROFILE%\.deno"

:: Verify Deno works
deno --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo ❌ Deno not working properly
    pause
    exit /b 1
)

echo [3/4] ✅ Environment ready

:: Check for cookies.txt
IF NOT EXIST "cookies.txt" (
    IF EXIST "yooutubecook.txt" (
        echo 📋 Found yooutubecook.txt, copying to cookies.txt...
        copy /Y "yooutubecook.txt" "cookies.txt" >nul
        echo ✅ Cookies file ready
    ) ELSE (
        echo ⚠️  Warning: No cookies.txt found
        echo YouTube downloads may require login
    )
)

echo [4/4] ✅ Ready to start
echo.
echo ============================================
echo Starting YouDub-webui...
echo ============================================
echo.

:: Run the application
python app.py

pause
