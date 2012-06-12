Redeal: a reimplementation of Thomas Andrews' Deal in Python.
=============================================================

Redeal runs under Python 2.7 or higher.  See script.py for an example
simulation.

GNU make and g++ are needed to build Bo Haglund's DDS v.1.1.9 (the latest
version I could find that can easily be built on Linux -- extracted and
slightly modified from the source of Thomas Andrews' Deal).  Simply run `make`
in the dds-1.1.9 folder.

Then run `./redeal.py --help`, or `./redeal.py` to get a few hands, or
`./redeal.py examples/deal1.py` for an example simulation.
`./run_all_examples.sh` will go through all the examples.
