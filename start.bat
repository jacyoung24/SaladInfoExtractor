@echo off

git pull
FOR /F %%i IN (dependencies.txt) DO @pip install %%i
pause
python SaladInfo.py
pause