@echo off

where >nul 2>nul py
if %ERRORLEVEL%==0 (set /A found_python = 1) else (set /A found_python = 0)

if %found_python%==1 (set "command=py -3") else (goto nopython)

(
echo @echo off
echo set oldcwd=%%cd%%
echo cd C:\Windows
echo %command% hail-files\hail.py %%1 %%2 %%3 %%oldcwd%%
echo cd %%oldcwd%%
) > C:\Windows\hail.bat

mkdir C:\Windows\hail-files
for %%X in (*.py) do type %%X > C:\Windows\hail-files\%%X

echo Installed hail!
goto:eof
nopython:
echo No python found installed!
exit /B