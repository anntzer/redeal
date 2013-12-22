#!/usr/bin/env python
from distutils.command.build_clib import build_clib
from setuptools import setup

import contextlib
import os
import subprocess
import sys
if sys.version_info.major < 3:
    from cStringIO import StringIO as BytesIO
    from urllib2 import urlopen, URLError
else:
    from io import BytesIO
    from urllib.request import urlopen, URLError
from zipfile import ZipFile


DDS_URL = "http://privat.bahnhof.se/wb758135/dds230-pbn-dll.zip"
if os.name == "posix":
    PACKAGE_DATA = [os.path.join("dds", "libdds.so")]
elif os.name == "nt":
    PACKAGE_DATA = [os.path.join("dds", "dds.dll")]
else:
    PACKAGE_DATA = []


class make_build(build_clib):
    def run(self):
        dirname = os.path.dirname(os.path.abspath(__file__))
        os.chdir(os.path.join(dirname, "redeal", "dds"))
        if os.name == "posix":
            subprocess.call("make")
        elif os.name == "nt":
            if not os.path.exists("dds.dll"):
                try:
                    with contextlib.closing(urlopen(DDS_URL)) as f:
                        zip_file = ZipFile(BytesIO(f.read()))
                        if zip_file.testzip() is not None:
                            print("Corrupted zip file, installation stopped.")
                            sys.exit(1)
                        zip_file.extract("dds.dll")
                        print("Successfully extracted dds.dll.")
                except URLError:
                    print("dds will not be available as I cannot download it.")
        else:
            print("dds will not be available as I don't know how to build it "
                  "on {}.  Please contact the author if you can help.".
                  format(os.name))
        os.chdir(dirname)


setup(
    cmdclass={"build_clib": make_build},
    name="redeal",
    version="0.2.0",
    author="Antony Lee",
    author_email="anntzer.lee@gmail.com",
    libraries=[("dds", {"sources": []})],
    packages=["redeal"],
    package_data={"redeal": PACKAGE_DATA},
    entry_points={"console_scripts": ["redeal = redeal.__main__:console_entry"],
                  "gui_scripts": ["redeal-gui = redeal.__main__:gui_entry"]},
    url="http://github.com/anntzer/redeal",
    license="LICENSE.txt",
    description="A reimplementation of Thomas Andrews' Deal in Python.",
    long_description=open("README.md").read(),
    requires=["colorama (>=0.2.4)"]
)
