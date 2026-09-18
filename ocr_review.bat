@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

set "PATH=C:\Program Files\nodejs;%APPDATA%\npm;%PATH%"

echo ==============================================================================
echo        ALIBABA OPEN-CODE-REVIEW - TEAM CAM GIANG SALES REPORT
echo ==============================================================================
echo.
echo [1] Xem truoc file can review: ocr delegate preview
echo [2] Kiem tra quy tac review cho file: ocr rules check [file]
echo [3] Chay AI Code Review tren thay doi chua commit: ocr review
echo [4] Quet toan bo ma nguon thu muc: ocr scan --path [dir]
echo [5] Cau hinh nha cung cap LLM: ocr config provider
echo [6] Mo giao dien truc quan xem lai phien: ocr viewer
echo [0] Thoat
echo.
set /p opt="Vui long chon tinh nang [0-6]: "

if "!opt!"=="1" goto do_preview
if "!opt!"=="2" goto do_check
if "!opt!"=="3" goto do_review
if "!opt!"=="4" goto do_scan
if "!opt!"=="5" goto do_config
if "!opt!"=="6" goto do_viewer
goto do_end

:do_preview
echo.
echo --- Danh sach file thay doi can review ---
ocr delegate preview
goto do_end

:do_check
echo.
set /p fpath="Nhap duong dan file (mac dinh: index.html): "
if "!fpath!"=="" set "fpath=index.html"
ocr rules check "!fpath!"
goto do_end

:do_review
echo.
echo Dang chay OCR Review...
ocr review --background "Du an Bao cao Doanh so CVS va BHX Team Cam Giang"
goto do_end

:do_scan
echo.
set /p spath="Nhap thu muc can quet (mac dinh: scripts): "
if "!spath!"=="" set "spath=scripts"
ocr scan --path "!spath!"
goto do_end

:do_config
echo.
echo Cau hinh nha cung cap LLM...
ocr config provider
goto do_end

:do_viewer
echo.
echo Dang khoi chay OCR Web Viewer...
ocr viewer
goto do_end

:do_end
echo.
echo ==============================================================================
pause
