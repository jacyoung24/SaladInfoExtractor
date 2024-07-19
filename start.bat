@echo off

git pull
IF NOT EXIST config.yml copy config-default.yml config.yml
FOR /F %%i IN (dependencies.txt) DO @pip install --disable-pip-version-check %%i
@REM pause
python SaladInfo.py
pause