
# MCP Break-Fix

An agent that tests an MCP server with attacks and faults, patches the code, and re-runs the same attacks to prove the fix works.

## Status
Work in progress.

- [✅] Phase 1: weak target server, manual client, manual attacks
- [ ] Phase 2: attack toolkit and pass/fail report
- [ ] Phase 3: normal-use tests and a throwaway-copy sandbox
- [ ] Phase 4: agent that picks and runs attacks
- [ ] Phase 5: fixer and verifier agents with human approval and PR creation
- [ ] Phase 6: report page and demo

## Project layout
- `targets/weak_server/`: the MCP server under test, with three planted bugs
- `scripts/`: manual client and a local slow server for the hang test
- `toolkit/`, `sandbox/`, `agents/`, `tests/`: added in later phases
- `NOTES.md`: learning log

## Run it locally
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/manual_client.py
```

For the hang test, start `python scripts/slow_server.py` in a second terminal first.