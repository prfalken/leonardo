# very very simple minded Makefile - may not be appropriate for you

NAME	= leonardo-build

BINDIR	= /usr/local/sbin
MANDIR	= /usr/local/share/man

all:
	echo nothing to make, just install

install:
	umask 022 && mkdir -p $(BINDIR)
	install -c -m 755 $(NAME) $(BINDIR)/$(NAME)
	umask 022 && mkdir -p $(MANDIR) $(MANDIR)/man8
	install -c -m 644 $(NAME).8 $(MANDIR)/man8/$(NAME).8

clean:
	echo nothing to clean, just install

