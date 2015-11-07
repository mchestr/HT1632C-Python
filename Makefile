CC=gcc
INCLUDES=-I. -I../..
LIBS=-L. -L../.. -L/usr/lib ../../libht1632c.a -lwiringPi

all: example1 example2 example3 example4

clean:
	rm -rf *.o example1 example2 example3 example4

example1: example1.o
	$(CC) -std=c99 -o $@ $^ $(LIBS)

example2: example2.o
	$(CC) -std=c99 -o $@ $^ $(LIBS)

example3: example3.o
	$(CC) -std=c99 -o $@ $^ $(LIBS)

example4: example4.o
	$(CC) -std=c99 -o $@ $^ $(LIBS)

%.o:	%.c
	$(CC) -std=c99 $(INCLUDES) -o $@ -c $^
