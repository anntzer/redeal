#!/usr/bin/env python
from distutils.core import setup
from distutils.command.build_clib import build_clib
import os
import subprocess


class make_build(build_clib):
    def run(self):
        os.chdir("redeal/dds-1.1.9")
        subprocess.call("make")
        os.chdir("../..")


setup(
    cmdclass={"build_clib": make_build},
    name="redeal",
    version="0.1.0",
    author="Antony Lee",
    author_email="anntzer.lee@gmail.com",
    libraries=[("dds", {"sources": []})],
    packages=["redeal"],
    package_data={"redeal": ["dds-1.1.9/libdds.so.1.1.9"]},
    entry_points={"console_scripts": ["redeal = redeal.__main__:main"]},
    url="http://github.com/anntzer/redeal",
    license="LICENSE.txt",
    description="A reimplementation of Thomas Andrews' Deal in Python.",
    long_description=open("README.md").read(),
)
