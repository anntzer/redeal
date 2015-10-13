@echo off
pushd %cd%
chdir %~dp0
chdir ..
for %%f in (examples\*.py) do (
echo %%f
python -m redeal %%f
)
popd
pause
