obj := main.o

mytestpackage: $(obj)
	$(CC) -o mytestpackage $(CFLAGS) $(LDFLAGS) $(obj)

$(obj): %.o : %.c
	$(CC) -c $(CFLAGS) $< -o $@

clean:
	rm -f mytestpackage