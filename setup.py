from __future__ import division, print_function
# for distutils compatibility we do not use unicode_literals in this module
from distutils.command.build_py import build_py
import io
import os
import shutil
import subprocess
import sys


def _abort(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)


try:
    from setuptools import setup
except ImportError:
    _abort("Please install setuptools by following the instructions at\n"
           "    https://pypi.python.org/pypi/setuptools")


if sys.platform == "win32":
    PACKAGE_DATA = ["dds-32.dll", "dds-64.dll"]
else:
    # On a POSIX system, libdds.so will be moved to its correct location by
    # make_build.
    PACKAGE_DATA = []


class make_build(build_py, object):
    def run(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        super(make_build, self).run()
        if sys.platform.startswith("linux") or sys.platform == "darwin":
            orig_dir = os.getcwd()
            try:
                os.chdir(os.path.join(base_dir, "dds", "src"))
            except OSError as exc:
                if exc.errno == 2:  # FileNotFoundError
                    _abort("""\
DDS sources are missing.

If you are using a git checkout, run
    git submodule init && git submodule update

On a Unix system, do not use the zip archives from github.""")
            if sys.platform.startswith("linux"):
                # Patch dds issue #91.
                with open("dds.cpp") as file:
                    contents = file.read()
                contents = contents.replace("FreeMemory();", "")
                with open("dds.cpp", "w") as file:
                    file.write(contents)
                subprocess.check_call([
                    "make", "THREADING=", "CC_BOOST_LINK=",
                    "-f", "Makefiles/Makefile_linux_shared",
                ])
            elif sys.platform == "darwin":
                with open("Makefiles/Makefile_Mac_clang") as file:
                    contents = file.read()
                contents = contents.replace(
                    "ar rcs $(STATIC_LIB) $(O_FILES)\n",
                    "$(CC) -dynamiclib -o lib$(DLLBASE).so $(O_FILES) -lc++\n")
                with open("Makefiles/Makefile_Mac_clang_patched", "w") as file:
                    file.write(contents)
                subprocess.check_call(
                    ["make", "-f", "Makefiles/Makefile_Mac_clang_patched",
                     "CC=gcc"])
                os.remove("Makefiles/Makefile_Mac_clang_patched")
            os.chdir(orig_dir)
            shutil.move(os.path.join(base_dir, "dds", "src", "libdds.so"),
                        os.path.join(self.build_lib, "redeal", "libdds.so"))


setup(
    cmdclass={"build_py": make_build},
    name="redeal",
    version="0.2.0",
    author="Antony Lee",
    author_email="anntzer.lee@gmail.com",
    packages=["redeal"],
    package_data={"redeal": PACKAGE_DATA},
    entry_points={
        "console_scripts": ["redeal = redeal.__main__:console_entry"],
        "gui_scripts": ["redeal-gui = redeal.__main__:gui_entry"],
    },
    url="http://github.com/anntzer/redeal",
    license="LICENSE.txt",
    description="A reimplementation of Thomas Andrews' Deal in Python.",
    long_description=io.open("README.rst", encoding="utf-8").read(),
    install_requires=
        ["colorama>=0.2.4"] +
        (["enum34>=1.0.4"] if sys.version_info < (3, 4) else [])
)
