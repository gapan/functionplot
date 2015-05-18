PREFIX ?= /usr/local
DESTDIR ?= /
PACKAGE_LOCALE_DIR ?= /usr/share/locale

help:
	@echo "make options are:"
	@echo " - make updatepo"
	@echo "     updates the po files"
	@echo " - make pot"
	@echo "     creates a new pot file from sources"
	@echo " - make mo"
	@echo "     creates .mo localization files in mo dir"
	@echo " - make clean"
	@echo "     cleans up everything"
	@echo " - make install"
	@echo "     installs in *nix systems"
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

mo:
	for i in `ls po/*.po | sed 's/.po//' | xargs -n1 basename` ;do \
			if [ ! -d mo/$$i/LC_MESSAGES ]; then \
					mkdir -p mo/$$i/LC_MESSAGES; \
			fi; \
			msgfmt -o mo/$$i/LC_MESSAGES/functionplot.mo po/$$i.po; \
	done

clean:
	rm -f po/*.mo
	rm -f po/*.po~
	rm -rf mo

install: install-mo
	python setup.py install --prefix=$(PREFIX) --root=$(DESTDIR)

install-mo: mo
	mkdir -p $(DESTDIR)$(PACKAGE_LOCALE_DIR)
	cp -r mo/* $(DESTDIR)$(PACKAGE_LOCALE_DIR)/

.PHONY: all mo updatepo pot clean install mo install-mo
