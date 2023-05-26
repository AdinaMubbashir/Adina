CC = clang
CFLAGS = -Wall -std=c99 -pedantic

PYTHON_INCLUDE_PATH = /usr/include/python3.7m
PYTHON_LIBRARY_PATH = /usr/lib/python3.7/config-3.7m-x86_64-linux-gnu
PYTHON_VERSION = python3.7m

all: libmol.so _molecule.so

clean:
	rm -f *.so *.o test1 test2 test3 molecule_wrap.c molecule.py main

main: clean all
	python3 MolDisplay.py

main-val: main
	valgrind --leak-check=full --show-leak-kinds=all --track-origins=yes ./main

libmol.so: mol.o
	$(CC) mol.o -shared -lm -o libmol.so

mol.o: mol.c mol.h
	$(CC) $(CFLAGS) -c mol.c -fPIC -o mol.o

molecule_wrap%c molecule%py: molecule.i mol.h
	swig -python molecule.i

molecule_wrap.o: molecule_wrap.c
	$(CC) $(CFLAGS) -c molecule_wrap.c -I$(PYTHON_INCLUDE_PATH) -fPIC -o molecule_wrap.o

_molecule.so:  molecule_wrap.o libmol.so
	$(CC) $(CFLAGS) -shared molecule_wrap.o -L. -L$(PYTHON_LIBRARY_PATH) -l$(PYTHON_VERSION) -lmol -dynamiclib -o _molecule.so