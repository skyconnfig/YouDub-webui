@echo off
chcp 65001 >nul
title YouDub 模型验证
echo.
echo ================================================
echo  YouDub 模型验证工具
echo ================================================
echo.
echo 正在检查本地模型...
echo.

python verify_models.py
