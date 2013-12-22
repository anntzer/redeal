UNAME := $(shell uname -s)
SONAME_FLAG := $(shell if [ `uname -s` = Darwin ]; \
    then echo dylib_install_name; else echo soname; fi)

all: libdds.so

libdds.so: dds.o
	$(CXX) -shared -Wl,-$(SONAME_FLAG),libdds.so.1 -lgomp -o $@ *.o

dds.o: dll.h dds.cpp
	$(CXX) -O3 -fPIC -D'itoa(value, str, base)=sprintf(str, "%d", value)' -c dds.cpp -o $@

clean:
	-rm dds.o libdds.so

.PHONY: clean
