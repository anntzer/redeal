Redeal: a reimplementation of Thomas Andrews' Deal in Python.
=============================================================

Redeal runs under Python 2.7 or higher.  See the examples/ folder for some
example simulations.

A double-dummy solver function is available through Bo Haglund's DDS v.1.1.9
(the latest version I could find that can easily be built on Linux -- extracted
and slightly modified from the source of Thomas Andrews' Deal), but you will
need a C++ compiler.  If you have g++ and make, simply run `make` in the
dds-1.1.9 folder; otherwise use the compiler of your choice.  If you cannot
compile the DDS library, Redeal will work fine but the `solve_board` function
will be unavailable.

Run `./redeal.py --help`, or `./redeal.py` to get a few hands, or `./redeal.py
examples/deal1.py` for an example simulation.  `./run_all_examples.sh` will go
through all the examples.
