#!/usr/bin/env sh
for f in `ls examples/*.py`; do echo $f; python redeal.py $f; done
