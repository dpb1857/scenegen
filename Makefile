# Install scenegen for all users on this Mac.
#
#   make deps            install Homebrew Python and Tk (run as yourself, not root)
#   sudo make install    install into $(PREFIX) and /Applications
#   sudo make uninstall  remove everything 'install' added
#   make check           check that an installed copy can run
#
# DESTDIR=/some/dir stages the install there (no root needed) for testing.

PREFIX     ?= /usr/local
BINDIR     := $(PREFIX)/bin
LIBDIR     := $(PREFIX)/lib/scenegen
APPDIR     ?= /Applications
APP        := $(APPDIR)/Scenegen.app

PYVERSION  ?= 3.15
PYPREFIX   ?= /opt/homebrew/opt/python@$(PYVERSION)
PYTHON     := $(PYPREFIX)/bin/python$(PYVERSION)
PYFRAMEWORK := $(PYPREFIX)/Frameworks/Python.framework/Versions/$(PYVERSION)
PYAPP_BIN  := $(PYFRAMEWORK)/Resources/Python.app/Contents/MacOS/Python

SLIDES_DIR := /Users/Shared/OBS/slides
SCENES_DIR := /Users/Shared/OBS/obs-studio/basic/scenes

SOURCES    := config.py google_drive.py google_sheets.py input_dialog.py \
              next_sunday.py process_util.py scenes.py validation.py

SUBST      := sed -e 's|@LIBDIR@|$(LIBDIR)|g' -e 's|@APP@|$(APP)|g' -e 's|@PYVERSION@|$(PYVERSION)|g'

.PHONY: all deps install uninstall check

all:
	@echo "Targets: deps, install, uninstall, check (see Makefile header)"

deps:
	@if [ "$$(id -u)" -eq 0 ]; then echo "Run 'make deps' as yourself, not root." >&2; exit 1; fi
	brew install python@$(PYVERSION) python-tk@$(PYVERSION)

install: apikey.py
	@if [ -z "$(DESTDIR)" ] && [ "$$(id -u)" -ne 0 ]; then echo "Run 'sudo make install'." >&2; exit 1; fi
	@if ! "$(PYTHON)" -c "import tkinter" 2>/dev/null; then \
	    echo "$(PYTHON) with Tk not found; run 'make deps' first." >&2; exit 1; fi
	install -d -m 755 "$(DESTDIR)$(BINDIR)" "$(DESTDIR)$(LIBDIR)"
	install -m 644 $(SOURCES) "$(DESTDIR)$(LIBDIR)/"
	install -m 644 apikey.py "$(DESTDIR)$(LIBDIR)/"
	"$(PYTHON)" -m venv --clear "$(DESTDIR)$(LIBDIR)/venv"
	"$(DESTDIR)$(LIBDIR)/venv/bin/pip" install --quiet --disable-pip-version-check -r requirements.txt
	"$(DESTDIR)$(LIBDIR)/venv/bin/python3" -m compileall -q "$(DESTDIR)$(LIBDIR)"
	$(SUBST) macos/scenegen-cli.in > "$(DESTDIR)$(BINDIR)/scenegen"
	chmod 755 "$(DESTDIR)$(BINDIR)/scenegen"
	rm -rf "$(DESTDIR)$(APP)"
	install -d -m 755 "$(DESTDIR)$(APP)/Contents/MacOS"
	install -d -m 755 "$(DESTDIR)$(APP)/Contents/Resources"
	install -m 644 macos/Info.plist "$(DESTDIR)$(APP)/Contents/Info.plist"
	install -m 644 macos/Scenegen.icns "$(DESTDIR)$(APP)/Contents/Resources/Scenegen.icns"
	$(SUBST) macos/Scenegen.in > "$(DESTDIR)$(APP)/Contents/MacOS/Scenegen"
	chmod 755 "$(DESTDIR)$(APP)/Contents/MacOS/Scenegen"
	@# Copy Homebrew's interpreter into the bundle (see macos/Scenegen.in), linked
	@# against the stable opt/ path so 'brew upgrade' within $(PYVERSION) keeps working.
	install -m 755 "$(PYAPP_BIN)" "$(DESTDIR)$(APP)/Contents/MacOS/Scenegen-python"
	old=$$(otool -L "$(PYAPP_BIN)" | awk 'NR > 1 && /Python.framework\/Versions/ {print $$1}'); \
	    install_name_tool -change "$$old" "$(PYFRAMEWORK)/Python" "$(DESTDIR)$(APP)/Contents/MacOS/Scenegen-python"
	codesign --force --sign - "$(DESTDIR)$(APP)/Contents/MacOS/Scenegen-python"
	@if [ ! -d "$(DESTDIR)$(SLIDES_DIR)" ]; then \
	    echo "install -d -m 775 $(DESTDIR)$(SLIDES_DIR)"; \
	    install -d -m 775 "$(DESTDIR)$(SLIDES_DIR)"; \
	    chgrp staff "$(DESTDIR)$(SLIDES_DIR)"; fi
	@echo "Installed. Run 'scenegen' or open $(APP) (drag it to the Dock to keep it there)."

apikey.py:
	@echo "apikey.py is missing; put it in this directory before installing." >&2
	@exit 1

uninstall:
	@if [ "$$(id -u)" -ne 0 ]; then echo "Run 'sudo make uninstall'." >&2; exit 1; fi
	rm -rf "$(LIBDIR)" "$(APP)"
	rm -f "$(BINDIR)/scenegen"
	@echo "Left $(SLIDES_DIR) in place."

check:
	@ok=1; \
	PYTHONPATH="$(LIBDIR)/venv/lib/python$(PYVERSION)/site-packages" \
	    "$(APP)/Contents/MacOS/Scenegen-python" -c "import tkinter, requests, psutil" 2>/dev/null \
	    && echo "ok: Python, Tk, requests, psutil" || { echo "FAIL: $(APP) or $(LIBDIR)/venv is missing or incomplete"; ok=0; }; \
	[ -r "$(LIBDIR)/apikey.py" ] && echo "ok: apikey.py" || { echo "FAIL: $(LIBDIR)/apikey.py not readable"; ok=0; }; \
	[ -r "$(SCENES_DIR)/templates.json" ] && echo "ok: templates.json" || { echo "FAIL: $(SCENES_DIR)/templates.json not readable"; ok=0; }; \
	for d in "$(SCENES_DIR)" "$(SLIDES_DIR)"; do \
	    [ -w "$$d" ] && echo "ok: $$d writable" || { echo "FAIL: $$d not writable by $$(id -un)"; ok=0; }; \
	done; \
	[ $$ok -eq 1 ]
