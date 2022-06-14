CC:= gcc
CFLAGS:= -O3 -D_POSIX_SOURCE -D_GNU_SOURCE -m64 -falign-functions=64 -Wall
LIBS:= -lpthread -lrt -lm
UTILS:= ../util/util.o ../util/msr-utils.o ../util/rapl-utils.o ../util/freq-utils.o

all: obj bin out data driver driver-input

driver: obj/driver.o $(UTILS)
	$(CC) -o bin/$@ $^ $(LIBS)

driver-input: obj/driver-input.o $(UTILS)
	$(CC) -o bin/$@ $^ $(LIBS)

obj/%.o: %.c
	$(CC) -c $(CFLAGS) -o $@ $<

obj:
	mkdir -p $@

bin:
	mkdir -p $@

out:
	mkdir -p $@

data:
	mkdir -p $@

clean:
	rm -rf bin obj out
	rm -rf ../util/*.o

.PHONY: all clean
