@echo off
chcp 65001 >nul
title YouDub 智能配置检测工具
echo.
echo ================================================
echo  🚀 YouDub 智能配置检测工具
echo ================================================
echo.
echo 正在检测你的硬件配置并生成最优参数...
echo.

python detect_optimal_config.py

echo.
echo ================================================
echo 检测完成！
echo ================================================
echo.
pause
