#!/bin/sh
cd $(dirname $(readlink -f $0))
cd ..
for f in `ls examples/*.py`; do echo $f; python -m redeal $f; done
