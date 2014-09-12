PLUGIN = markdown

VERSION = 0.1.0

ifndef PYTHON3
PYTHON3 = python3
endif

OUTPUT_SOURCES = app.py __init__.py settings.py settings.ui win.py
OUTPUT = markdown.plugin

ICON_128_DIR = ~/.local/share/icons/hicolor/128x128/apps
ICON_48_DIR = ~/.local/share/icons/hicolor/48x48/apps

all: markdown.plugin

markdown.plugin: markdown.plugin.m4 Makefile
	@ type m4 > /dev/null || ( echo 'm4 is missing and is required to build Valencia. ' ; exit 1 )
	m4 -DVERSION='$(VERSION)' markdown.plugin.m4 > markdown.plugin

install:
	@ [ `whoami` != "root" ] || ( echo 'Run make install as yourself, not as root.' ; exit 1 )
	mkdir -p ~/.local/share/gedit/plugins/gedit-markdown
	cp $(OUTPUT_SOURCES) ~/.local/share/gedit/plugins/gedit-markdown
	mkdir -p ~/.local/share/gedit/plugins
	cp $(OUTPUT) ~/.local/share/gedit/plugins
	mkdir -p $(ICON_128_DIR)
	cp -p icons/gmarkdown-128.png $(ICON_128_DIR)/gmarkdown.png
	mkdir -p $(ICON_48_DIR)
	cp -p icons/gmarkdown-48.png $(ICON_48_DIR)/gmarkdown.png

uninstall:
	rm -f $(foreach o, $(OUTPUT_SOURCES), ~/.local/share/gedit/plugins/gedit-markdown/$o)
	rm -f ~/.local/share/gedit/plugins/$(OUTPUT)
	rm -f $(ICON_128_DIR)/gmarkdown.png
	rm -f $(ICON_48_DIR)/gmarkdown.png

clean:
	rm -f markdown.plugin
