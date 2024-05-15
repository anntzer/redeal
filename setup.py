import contextlib
from contextlib import ExitStack
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import shutil
import subprocess
import sys
import urllib.request

import setuptools.command.build_ext


@contextlib.contextmanager
def patched_path(path, old, new):
    contents = path.read_text("latin-1")
    if old not in contents:
        raise Exception(f"Invalid patch: {old}")
    try:
        path.write_text(contents.replace(old, new), "utf-8")
        yield
    finally:
        path.write_text(contents, "latin-1")


patches = [
    ("Makefiles/Makefile_linux_shared",
     "$(COMPILE_FLAGS)", "$(COMPILE_FLAGS) $(CFLAGS)"),
    ("Makefiles/Makefile_Mac_clang_shared",
     "$(COMPILE_FLAGS)", "$(COMPILE_FLAGS) $(CFLAGS)"),
    ("Makefiles/Makefile_Mac_clang_shared",
     "-Wextra", "-Wextra -Wno-deprecated-declarations -Wno-sign-conversion"),
    ("Makefiles/Makefile_Mac_clang_shared",
     "$(LINK_FLAGS)", "$(LINK_FLAGS) -lc++"),
    ("TransTableL.cpp",
     "const unsigned char lengths[][DDS_SUITS]) const",
     "const unsigned char lengths[DDS_SUITS][DDS_SUITS]) const"),
    ("Moves.cpp", "", ""),  # Only for reencoding.
]


class build_ext(setuptools.command.build_ext.build_ext):
    def finalize_options(self):
        super().finalize_options()
        # Needs to be computed here because setuptools patches out inplace.
        self.__dest_dir = Path(self.get_ext_fullpath("redeal._")).parent

    def build_extensions(self):
        self.distribution.ext_modules[:] = []
        super().build_extensions()
        if os.name == "posix":
            dds_src = Path(__file__).resolve().parent / "dds/src"
            if not dds_src.exists():
                sys.exit("""\
DDS sources are missing.

If you are using a git checkout, run
    git submodule init && git submodule update

On a Unix system, do not use the zip archives from github.""")
            with ExitStack() as stack:
                for name, old, new in patches:
                    stack.enter_context(patched_path(dds_src / name, old, new))
                if sys.platform.startswith("linux"):
                    subprocess.check_call(
                        ["make", "-f", "Makefiles/Makefile_linux_shared",
                         "THREADING=", "THREAD_LINK="], cwd=dds_src)
                elif sys.platform == "darwin":
                    subprocess.check_call(
                        ["make", "-f", "Makefiles/Makefile_Mac_clang_shared",
                         "CC=gcc", "THREADING=", "THREAD_LINK="], cwd=dds_src)
            shutil.copy2(dds_src / "libdds.so", self.__dest_dir)
        elif os.name == "nt":
            url = "https://privat.bahnhof.se/wb758135/bridge/dds290-dll.zip"
            with TemporaryDirectory() as tmpdir:
                tmppath = Path(tmpdir)
                zip_path = tmppath / "dds290-dll.zip"
                with urllib.request.urlopen(url) as req:
                    zip_path.write_bytes(req.read())
                shutil.unpack_archive(str(zip_path), tmpdir)  # str() for Py36.
                arch = "x64" if sys.maxsize > 2 ** 32 else "win32"
                shutil.unpack_archive(
                    str(tmppath / f"dds290-dll/dds-290-multi-{arch}-dll.zip"),
                    tmppath)
                shutil.copy2(tmppath / "dds.dll", self.__dest_dir)


setuptools.setup(
    cmdclass={"build_ext": build_ext},
    ext_modules=[setuptools.Extension("", [])],
    packages=["redeal"],
)
