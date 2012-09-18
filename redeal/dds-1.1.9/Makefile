UNAME := $(shell uname -s)
SONAME_FLAG := $(shell if [ `uname -s` = Darwin ]; \
    then echo dylib_install_name; else echo soname; fi)

all: libdds.so.1.1.9

libdds.so.1.1.9: dds.o ddsLookup.o
	$(CXX) -shared -Wl,-$(SONAME_FLAG),libdds.so.1 -o $@ *.o

.cpp.o:
	$(CXX) -O3 -fPIC -c $< -o $@

clean:
	-rm *.o libdds.so.1.1.9

.PHONY: clean
