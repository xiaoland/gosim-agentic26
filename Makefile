PYTHON ?= python3
PORT ?= 8146
SHOT ?= build/debug.png
OCTO = $(PYTHON) tools/octo
AGENT = $(PYTHON) tools/agent.py

.PHONY: bootstrap doctor run dev run-hidden logs tree check shot smoke
bootstrap:
	$(PYTHON) tools/bootstrap.py
doctor:
	$(OCTO) doctor
run:
	$(OCTO) run bundle --port $(PORT)
dev:
	$(OCTO) run bundle --port $(PORT) --detach
run-hidden:
	$(OCTO) run bundle --port $(PORT) --hidden --detach
logs:
	$(PYTHON) -c 'import json; from urllib.request import urlopen; print("\n".join(json.load(urlopen("http://127.0.0.1:$(PORT)/log?n=100", timeout=5))["l"]))'
tree:
	curl --fail --silent --show-error --max-time 5 'http://127.0.0.1:$(PORT)/d'
check:
	$(OCTO) check bundle
shot:
	$(OCTO) shot $(PORT) "$(SHOT)"
smoke:
	$(PYTHON) tools/smoke.py

.PHONY: agent-bootstrap agent-doctor agent-init-demo agent-dev agent-hidden agent-stop agent-status agent-tree agent-logs agent-shot
agent-bootstrap:
	$(AGENT) bootstrap
agent-doctor:
	$(AGENT) doctor
agent-init-demo:
	$(AGENT) init-demo
agent-dev:
	$(AGENT) dev
agent-hidden:
	$(AGENT) hidden
agent-stop:
	$(AGENT) stop
agent-status:
	$(AGENT) status
agent-tree:
	$(AGENT) tree
agent-logs:
	$(AGENT) logs
agent-shot:
	$(AGENT) shot --output "$(SHOT)"
