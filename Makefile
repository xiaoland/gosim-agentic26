PYTHON ?= python3
PORT ?= 8146
OCTO = $(PYTHON) tools/octo

.PHONY: bootstrap doctor run run-hidden check shot smoke
bootstrap:
	$(PYTHON) tools/bootstrap.py
doctor:
	$(OCTO) doctor
run:
	$(OCTO) run bundle --port $(PORT)
run-hidden:
	$(OCTO) run bundle --port $(PORT) --hidden --detach
check:
	$(OCTO) check bundle
shot:
	$(OCTO) shot $(PORT) bundle/screenshots/01-main.png
smoke:
	$(PYTHON) tools/smoke.py
