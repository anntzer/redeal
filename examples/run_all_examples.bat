@echo off
for %%f in (*.py) do (
echo %%f
python redeal.py %%f
)
pause
