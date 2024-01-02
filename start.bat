echo off

git pull
FOR /F %%i IN (dependencies.txt) DO @pip install %%i
timeout 5
python SaladInfo.py