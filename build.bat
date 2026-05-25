@echo off
echo ========================================
echo DataMatrix Quality Scanner - Build Script
echo ========================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10 or higher from https://python.org
    pause
    exit /b 1
)

echo [*] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo [*] Installing PyInstaller...
pip install pyinstaller
if errorlevel 1 (
    echo ERROR: Failed to install PyInstaller
    pause
    exit /b 1
)

echo [*] Creating resources directory...
if not exist "resources" mkdir resources
if not exist "resources\sounds" mkdir resources\sounds

echo.
echo ========================================
echo Building EXE...
echo ========================================
echo.

REM Clean previous builds
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build

REM Build with PyInstaller
pyinstaller datamatrix_scanner.spec --clean

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build completed successfully!
echo ========================================
echo.
echo EXE location: dist\DataMatrixScanner.exe
echo.
echo To run the application:
echo   dist\DataMatrixScanner.exe
echo.
echo Press any key to open the dist folder...
pause >nul
explorer dist

exit /b 0