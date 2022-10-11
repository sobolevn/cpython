#
# Makefile for Python property-based-testing
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#

# You can set these variables from the command line.
PYTHON       = python3
VENVDIR      = ./venv

.PHONY: venv test

clean-venv:
	rm -rf $(VENVDIR)

venv:
	@if [ -d $(VENVDIR) ] ; then \
		echo "venv already exists."; \
		echo "To recreate it, remove it first with \`make clean-venv'."; \
	else \
		$(PYTHON) -m venv $(VENVDIR); \
		$(VENVDIR)/bin/python3 -m pip install -U pip setuptools; \
		$(VENVDIR)/bin/python3 -m pip install -r requirements.txt; \
		echo "The venv has been created in the $(VENVDIR) directory"; \
	fi

test:
	$(VENVDIR)/bin/python3 -m unittest discover ./tests
