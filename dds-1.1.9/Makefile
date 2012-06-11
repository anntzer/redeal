all: libdds.so.1.1.9

libdds.so.1.1.9: dds.o ddsLookup.o
	g++ -shared -Wl,-soname,libdds.so.1 -o $@ *.o

.cpp.o:
	g++ -O3 -fPIC -c $< -o $@

clean:
	-rm *.o libdds.so.1.1.9

.PHONY: clean
