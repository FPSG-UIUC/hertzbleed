CC:= gcc
CFLAGS:= -O3 -D_POSIX_SOURCE -D_GNU_SOURCE -m64
LIBS:= -lpthread -lrt

all: obj bin out sender receiver

sender: obj/sender.o ../util/util.o
	$(CC) -o bin/$@ $^ $(LIBS)

receiver: obj/receiver.o ../util/util.o ../util/msr-utils.o ../util/freq-utils.o
	$(CC) -o bin/$@ $^ $(LIBS)

obj/%.o: %.c
	$(CC) -c $(CFLAGS) -o $@ $<

obj:
	mkdir -p $@

bin:
	mkdir -p $@

out:
	mkdir -p $@

clean:
	rm -rf bin obj

.PHONY: all clean
