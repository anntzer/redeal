#!/usr/bin/env sh
for f in `ls *.py`; do echo $f; python ../redeal/redeal.py $f; done
