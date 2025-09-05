@echo off
chcp 65001 >nul
echo ================================================================
echo                    VPSX.ME TRAFFIC SIMULATOR
echo ================================================================
echo.

:menu
echo Chọn chế độ chạy:
echo 1. Demo Mode (3 visits để test)
echo 2. Full Simulation (chạy liên tục)
echo 3. Custom Demo (nhập số visits)
echo 4. Thoát
echo.

set /p choice="Nhập lựa chọn (1-4): "

if "%choice%"=="1" goto demo
if "%choice%"=="2" goto full
if "%choice%"=="3" goto custom
if "%choice%"=="4" goto exit
echo Lựa chọn không hợp lệ!
goto menu

:demo
echo.
echo 🚀 Chạy Demo Mode (3 visits)...
python browser_simulator.py demo 3
pause
goto menu

:full
echo.
echo 🚀 Chạy Full Simulation...
echo ⚠️  Nhấn Ctrl+C để dừng
echo.
python browser_simulator.py
pause
goto menu

:custom
echo.
set /p visits="Nhập số visits: "
echo 🚀 Chạy Demo với %visits% visits...
python browser_simulator.py demo %visits%
pause
goto menu

:exit
echo.
echo 👋 Tạm biệt!
timeout 2 >nul
