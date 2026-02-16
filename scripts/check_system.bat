@echo off
chcp 65001 >nul
echo ============================================
echo 系统配置检测工具
echo ============================================
echo.

echo [正在检测系统配置...]
echo.

REM CPU 信息
echo 【CPU 信息】
wmic cpu get Name, NumberOfCores, NumberOfLogicalProcessors /format:value 2>nul | findstr /V "^$"
echo.

REM 内存信息
echo 【内存信息】
for /f "skip=1 tokens=*" %%a in ('wmic ComputerSystem get TotalPhysicalMemory') do (
    if not defined MEM (
        set "MEM=%%a"
        set /a MEM_GB=%%a / 1024 / 1024 / 1024
        echo 总内存: !MEM_GB! GB
    )
)
echo.

REM 显卡信息
echo 【显卡信息】
wmic path win32_VideoController get Name, AdapterRAM /format:value 2>nul | findstr /V "^$"
echo.

REM 硬盘信息
echo 【硬盘空间】
for /f "tokens=3" %%a in ('wmic logicaldisk where "DeviceID='D:'" get FreeSpace /value ^| find "="') do (
    set /a FREE_D=%%a / 1024 / 1024 / 1024
    echo D盘剩余空间: !FREE_D! GB
)
for /f "tokens=3" %%a in ('wmic logicaldisk where "DeviceID='C:'" get FreeSpace /value ^| find "="') do (
    set /a FREE_C=%%a / 1024 / 1024 / 1024
    echo C盘剩余空间: !FREE_C! GB
)

echo.
echo ============================================
echo 按任意键关闭...
pause >nul
