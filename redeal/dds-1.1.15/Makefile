UNAME := $(shell uname -s)
SONAME_FLAG := $(shell if [ `uname -s` = Darwin ]; \
    then echo dylib_install_name; else echo soname; fi)

all: libdds.so.1.1.15

libdds.so.1.1.15: dds.o
	$(CXX) -shared -Wl,-$(SONAME_FLAG),libdds.so.1 -o $@ *.o

dds.o: dds.cpp dll.h patched
	$(CXX) -O3 -fPIC -c $< -o $@

patched: dds.patch
	patch -b <dds.patch
	touch patched

clean:
	-mv -f dds.cpp.orig dds.cpp
	-mv -f dll.h.orig dll.h
	-rm patched *.o libdds.so.1.1.15

.PHONY: clean
