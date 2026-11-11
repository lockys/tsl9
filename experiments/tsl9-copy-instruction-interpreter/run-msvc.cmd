@echo off
setlocal
cd /d "%~dp0\..\.."
if not defined VSCMD_VER (
  echo Run from an MSVC developer command prompt. 1>&2
  exit /b 1
)
set "COPY_C_ORACLE=%TEMP%\tsl9-copy-oracle.exe"
cl /nologo /W4 /I experiments\tsl9-resident-copy-reference\src /I experiments\tsl9-boot2580-uid-helper\src /I experiments\tsl9-boot2580-command-adapter\src experiments\tsl9-copy-instruction-interpreter\c_oracle.c experiments\tsl9-resident-copy-reference\src\reference_copy.c /Fe:"%COPY_C_ORACLE%" /Fo:"%TEMP%\\"
if errorlevel 1 exit /b 1
python experiments\tsl9-copy-instruction-interpreter\test_interpreter.py
if errorlevel 1 exit /b 1
python experiments\tsl9-copy-instruction-interpreter\test_rf_integration.py
if errorlevel 1 exit /b 1
