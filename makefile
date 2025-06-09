PREFIX		?= /usr/local

install:
	install -Dm 755 ./corth $(DESTDIR)$(PREFIX)/bin/corth

uninstall:
	rm -f $(DESTDIR)$(PREFIX)/bin/corth
