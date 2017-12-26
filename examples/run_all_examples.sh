#!/bin/sh
set -e
# May fail if someone has this in his $PATH, but readlink -f doesn't work on
# Mac OS, so at least it's portable.
cd "$(dirname "$(pwd)/$0")"
for f in *.py; do echo $f; ${PYTHON:-python} -m redeal $f; done
