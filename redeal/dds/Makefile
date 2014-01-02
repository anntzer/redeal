UNAME := $(shell uname -s)
SONAME_FLAG := $(shell if [ `uname -s` = Darwin ]; \
    then echo dylib_install_name; else echo soname; fi)

all: libdds.so

libdds.so: dds.o
	$(CXX) -shared -Wl,-$(SONAME_FLAG),libdds.so.1 -lgomp -o $@ *.o

dds.o: dll.h dds.cpp
	$(CXX) -O3 -fPIC -DPBN -DPBN_PLUS \
	    -D'itoa(value, str, base)=(base == 10 ? sprintf(str, "%d", value) : (exit(1), 0))' \
	    -c dds.cpp -o $@

clean:
	-rm dds.o libdds.so

.PHONY: clean
