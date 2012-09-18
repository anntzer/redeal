@echo off
cd ..
for %%f in (*.py) do (
echo %%f
python -m redeal %%f
)
pause
