UNAME := $(shell uname -s)
SONAME_FLAG := $(shell if [ `uname -s` = Darwin ]; \
    then echo dylib_install_name; else echo soname; fi)

all: libdds.so

libdds.so: dds.o
	$(CXX) -shared -Wl,-$(SONAME_FLAG),libdds.so.1 -o $@ *.o

dds.o: patched
	$(CXX) -O3 -fPIC -c dds.cpp -o $@

patched: dds.patch
	cp ../dds-src/dds.cpp .
	cp ../dds-src/dll.h .
	patch -b <dds.patch
	touch patched

clean:
	-rm dds.cpp dds.cpp.orig dll.h dll.h.orig
	-rm patched dds.o libdds.so

.PHONY: clean
