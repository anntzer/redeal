import os
import sys
from cx_Freeze import setup, Executable

assert sys.platform == "win32"

setup(
    name="redeal",
    version="0.2.0",
    author="Antony Lee",
    author_email="anntzer.lee@gmail.com",
    libraries=[("dds", {"sources": []})],
    packages=["redeal"],
    options={
        "build_exe": {
            "include_files": [os.path.join("redeal", "dds", "dds.dll")]}},
    executables=[Executable("freeze_executable.py", base="Win32GUI")],
    url="http://github.com/anntzer/redeal",
    license="LICENSE.txt",
    description="A reimplementation of Thomas Andrews' Deal in Python.",
    long_description=open("README.md").read(),
)
