#!/bin/sh
cd ..
for f in `ls examples/*.py`; do echo $f; python -m redeal $f; done
