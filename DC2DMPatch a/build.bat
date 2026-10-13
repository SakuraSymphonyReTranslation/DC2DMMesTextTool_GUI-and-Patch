@echo off
setlocal
pushd "%~dp0"
echo Building Da Capo 2 Dearest Marriage patch and launcher...
cmake -S . -B build -G "Visual Studio 17 2022" -A Win32
if errorlevel 1 goto failed
cmake --build build --config Release
if errorlevel 1 goto failed
if not exist "build\Released" mkdir "build\Released"
copy /Y "build\Release\DC2DMPatch.dll" "build\Released\DC2DMPatch.dll" >nul
if errorlevel 1 goto failed
copy /Y "build\Release\DC2DMLauncher.exe" "build\Released\DC2DMLauncher.exe" >nul
if errorlevel 1 goto failed
echo Ready: build\Released\DC2DMPatch.dll and DC2DMLauncher.exe
popd
exit /b 0
:failed
popd
exit /b 1
