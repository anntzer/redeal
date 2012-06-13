@echo off
for %%f in (examples/*.py) do (
echo %%f
python redeal.py examples/%%f
)
pause
