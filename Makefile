PREFIX ?= /usr/local
DESTDIR ?= /
PACKAGE_LOCALE_DIR ?= /usr/share/locale

help:
	@echo "make options are:"
	@echo " - make updatepo"
	@echo " - make pot"
	@echo " - make clean"
	@echo " - make install"
	@echo ""
	@echo "You can specify DESTDIR, PREFIX and PACKAGE_LOCALE_DIR variables"

updatepo:
	for i in `ls po/*.po`; do \
		msgmerge -UNs $$i po/functionplot.pot; \
	done

pot:
	xgettext --from-code=utf-8 \
		-L Glade \
		-o po/functionplot.pot \
		functionplot/functionplot.glade
	xgettext --from-code=utf-8 \
		-j \
		-L python \
		-o po/functionplot.pot \
		functionplot/functionplot.py

clean:
	rm -f po/*.mo
	rm -f po/*.po~

install: install-mo
	python setup.py --prefix=$(PREFIX) --root=$(DESTDIR)

install-mo:
	for i in `ls po/*.po | sed 's/.po//' | xargs -n1 basename` ;do \
			if [ ! -d $(DESTDIR)$(PACKAGE_LOCALE_DIR)/$$i/LC_MESSAGES ]; then \
					mkdir -p $(DESTDIR)$(PACKAGE_LOCALE_DIR)/$$i/LC_MESSAGES; \
			fi;\
			msgfmt -o $(DESTDIR)$(PACKAGE_LOCALE_DIR)/$$i/LC_MESSAGES/functionplot.mo po/$$i.po; \
	done

.PHONY: all mo updatepo pot clean install install-mo
