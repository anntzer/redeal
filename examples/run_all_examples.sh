#!/bin/sh
cd $(dirname $(readlink -f $0))
cd ..
for f in `ls examples/*.py`; do echo $f; ${PYTHON:-python} -m redeal $f; done
