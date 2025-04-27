
APP_MODULE = main:app
SRC_DIR = src
activate = export PYTHONPATH="src:$$PYTHONPATH"

run:
	$(activate) && venv/bin/python src/main.py



.PHONY: run
