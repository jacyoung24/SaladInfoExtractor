@echo off

git pull
IF NOT EXIST config.yml copy config-default.yml config.yml
FOR /F %%i IN (dependencies.txt) DO @pip install %%i
pause
python SaladInfo.py
pause