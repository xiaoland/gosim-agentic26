# Developing this OctoSense app

> **Any coding agent, or none.** These instructions work the same for Codex, Claude Code, Cursor, Gemini CLI, GitHub Copilot or a person at a terminal: every step is a shell command or a file edit, and nothing here needs a particular agent, model or vendor. `AGENTS.md` is the one source of truth; `CLAUDE.md` and `GEMINI.md` only import it for agents that look for those names.

This repository is one OctoSense script app. `bundle/` is the app and the only
thing submitted to the App Hub; everything else stays outside it.

Follow the harness, and do not invent requirements or APIs:

- How to build, run and test: [QUICKSTART](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/main/docs/QUICKSTART.md)
- The language and every API an app may use: [SCRIPT-API](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/main/docs/SCRIPT-API.md)
- Capabilities: [CAPABILITIES](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/main/docs/CAPABILITIES.md)
- Publishing, step by step, with the human checkpoints: [PUBLISHING](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/main/docs/PUBLISHING.md)

The loop, with `OCTO=<path to OctoScript-App-Design-Flow>/tools/octo` (the CLI
lives in the harness repository, not here), run from this directory: edit
`bundle/main.splash` → `$OCTO run bundle --port 8141 --detach` → drive it
(`/click`, `/t`, `/snap`) and `$OCTO shot 8141 out.png` → `curl -s 127.0.0.1:8141/quit`
→ `$OCTO check bundle`.

Rules:

- Ask only for capabilities a screen uses; declare every `https://` host in
  `network.hosts`; never `http://`.
- Never collect a password, PIN or code; accounts go through a host service.
- Screenshots are real captures you looked at. Never a dummy.
- Restamp after every edit (`tools/octo check` does it). After signing, any
  edit needs a new stamp and signature.
- Keys, `.local-state/`, `build/` and review packets never enter `bundle/` or git.
- Stop at human steps: publisher key, publisher details, platform claims, submission.

Add this app's own requirements, data sources and tests below.

## Navigation repository scope

- Read BRIEF.md and docs/architecture.md before changing behavior. The confirmed core is lowest-cost mixed transport within a time limit, including taxi legs.
- This is currently initialization only. Do not present the draft UI as a working route planner or complete contest entry.
- Use `make bootstrap`, `make doctor`, `make smoke`, `make check`. Source versions are in toolchain/sources.lock.json.
- Run native checks hidden, use isolated app data, and close only processes started by the test.
- `bundle/` contains only runtime files. Keep toolchain, secrets, logs and review packets outside it.
- LLMs interpret constraints and explain results; the future deterministic planner computes routes and cost. Preserve evidence of data source, timestamp and expiry.
- Latest verified scope: macOS arm64 card-host only. Publisher metadata is intentionally pending for later publication.
- Do not treat private ChatGPT discussions as official competition rules; docs/sources.md records primary sources.
