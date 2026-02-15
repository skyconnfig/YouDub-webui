@echo off
chcp 65001 >nul
echo ==========================================
echo YouDub 快速模式配置切换工具
echo ==========================================
echo.
echo 选择模式：
echo [1] 极速模式 - 3-5分钟/视频（适合预览）
echo [2] 平衡模式 - 6-10分钟/视频（推荐日常使用）
echo [3] 质量模式 - 15-20分钟/视频（最终发布）
echo [4] 自定义配置
echo.
set /p choice="请输入数字 (1-4): "

if "%choice%"=="1" goto fast
if "%choice%"=="2" goto balanced
if "%choice%"=="3" goto quality
if "%choice%"=="4" goto custom
goto end

:fast
echo.
echo 【极速模式配置】
echo - 分辨率: 720p
echo - Demucs Model: htdemucs
echo - Shifts: 0
echo - Whisper Model: small
echo - Batch Size: 64
echo - 说话人分离: 关闭
echo - 并行处理: 3个视频
echo.
echo 请在 Gradio 界面中按以下设置：
echo Resolution: 720p
echo Demucs Model: htdemucs
echo Number of shifts: 0
echo Whisper Model: small
echo Whisper Batch Size: 64
echo Whisper Diarization: False
echo Max Workers: 3
echo.
pause
goto end

:balanced
echo.
echo 【平衡模式配置】（推荐）
echo - 分辨率: 1080p
echo - Demucs Model: htdemucs_ft
echo - Shifts: 1
echo - Whisper Model: medium
echo - Batch Size: 32
echo - 说话人分离: 关闭
echo - 并行处理: 2个视频
echo.
echo 请在 Gradio 界面中按以下设置：
echo Resolution: 1080p
echo Demucs Model: htdemucs_ft
echo Number of shifts: 1
echo Whisper Model: medium
echo Whisper Batch Size: 32
echo Whisper Diarization: False
echo Max Workers: 2
echo.
pause
goto end

:quality
echo.
echo 【质量模式配置】
echo - 分辨率: 1080p
echo - Demucs Model: htdemucs_ft
echo - Shifts: 5
echo - Whisper Model: large
echo - Batch Size: 16
echo - 说话人分离: 开启
echo - 并行处理: 1个视频
echo.
echo 请在 Gradio 界面中按以下设置：
echo Resolution: 1080p
echo Demucs Model: htdemucs_ft
echo Number of shifts: 5
echo Whisper Model: large
echo Whisper Batch Size: 16
echo Whisper Diarization: True
echo Max Workers: 1
echo.
pause
goto end

:custom
echo.
echo 【自定义配置建议】
echo.
echo 最重要的优化参数（按影响排序）：
echo.
echo 1. Number of shifts (Demucs)
echo    - 0: 最快，质量稍降
echo    - 1-2: 平衡
echo    - 5: 最慢，质量最高
echo.
echo 2. Whisper Model
echo    - tiny: 极快，质量较低
echo    - small: 快，质量可接受
echo    - medium: 平衡（推荐）
echo    - large: 慢，质量最高
echo.
echo 3. Whisper Diarization
echo    - False: 节省30-50%%时间
echo    - True: 需要多说话人识别时开启
echo.
echo 4. Max Workers
echo    - 根据显存设置：
echo    - 8GB显存: 1
echo    - 16GB显存: 2
echo    - 24GB+显存: 3-5
echo.
pause
goto end

:end
echo.
echo 提示：运行 python app.py 后在 Gradio 界面中设置参数
echo.
