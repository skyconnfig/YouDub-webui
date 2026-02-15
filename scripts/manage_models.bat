@echo off
chcp 65001 >nul
title YouDub 模型管理工具
echo.
echo ================================================
echo  YouDub 模型管理工具
echo ================================================
echo.
echo [1] 查看模型状态
echo [2] 迁移系统缓存到本地
echo [3] 下载Whisper模型
echo [4] 清理系统缓存
echo [5] 退出
echo.
set /p choice="选择操作 (1-5): "

if "%choice%"=="1" goto info
if "%choice%"=="2" goto migrate
if "%choice%"=="3" goto download
if "%choice%"=="4" goto clean
if "%choice%"=="5" goto end
goto end

:info
cls
python manage_models.py info
echo.
pause
goto menu

:migrate
cls
python manage_models.py migrate
echo.
pause
goto menu

:download
cls
echo 可用模型: tiny, base, small, medium, large
echo 推荐: medium (平衡) 或 small (快速)
set /p model="输入模型名称 (默认 medium): "
if "%model%"=="" set model=medium
python manage_models.py download %model%
echo.
pause
goto menu

:clean
cls
echo 警告: 这将删除系统缓存中的模型文件!
echo 本地模型不会被删除。
echo.
set /p confirm="确认删除? (yes/no): "
if "%confirm%"=="yes" python manage_models.py clean
echo.
pause
goto menu

:menu
cls
goto start

:start
python manage_models.py
goto end

:end
echo.
echo 感谢使用!
echo.
pause
