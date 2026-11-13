# Learning Log

## Phase 1: Weak server and manual attacks

Target: `targets/weak_server/server.py`, an MCP server with three tools and one planted bug each. All results matched my predictions.

### Attack 1: Path traversal (`read_note`)
- **Sent:** `filename = "../secret.txt"`
- **Predicted:** the `..` would climb out of `notes/` and read a file the tool should never touch.
- **What happened:** the server returned the contents of `secret.txt` as a normal successful result, with no error and no warning.
- **Why it worked:** `(NOTES_DIR / filename).read_text()` joins user text straight onto the folder path and never checks where the final path lands.
- **One-line check:** resolve the final path and refuse it unless it is inside the notes folder, using `.resolve()` and `.is_relative_to(NOTES_DIR.resolve())`.

### Attack 2: Code injection (`calculate`)
- **Sent:** `2 + 2` as a baseline, then `__import__('os').listdir('.')`.
- **Predicted:** the baseline returns 4, and the second input runs as real Python instead of being rejected as "not math".
- **What happened:** the baseline returned 4, and the second call returned a list of files from the server's working folder.
- **Why it worked:** `eval(expression)` executes any Python expression. The tool description says "math", but nothing in the code enforces that.
- **One-line check:** stop using `eval`. Parse the input with `ast` and allow only numbers and the operators `+ - * /`.

### Attack 3: Hang and local access (`fetch_url`)
- **Sent:** `http://127.0.0.1:9999`, a local server that sleeps for 5 minutes before answering.
- **Predicted:** the client would freeze, and the tool would happily call a local address.
- **What happened:** the call blocked for about 5 minutes and then returned `late`. It also reached a server on my own machine without complaint.
- **Why it worked:** two separate bugs on one line. `timeout=None` means wait forever, and there is no restriction on which addresses can be fetched.
- **One-line check:** set a short timeout such as `timeout=5`, allow only `http`/`https`, and block localhost and private IP ranges.

## What I learned
- An MCP server runs as a subprocess and talks to the client over stdio.
- The agent only sees each tool's name, description and input schema. It cannot see the code, so a description like "math expression" promises something the code may not enforce.
- All three failures looked like success from the client side. The secret was returned as a normal result, which is why a tester has to check the content of results, not just whether the call errored.
- A hung tool call blocks the whole client, so every attack needs a timeout on the tester's side too.
- Each bug has a small, specific fix. That is what makes automated fixing realistic later.

## Ideas for later phases
- A fixed copy of the server to compare against the weak one.
- A set of normal-use checks, so a fix that breaks real behavior gets caught.
- Attack results should record the evidence (what came back), not just pass or fail.




## Phase 2, Day 6: Broadening the attack cases

### What changed
- Went from 4 attack cases to 11, covering path traversal, calculator abuse and fetch abuse.
- Added three traversal variants (`../`, deeper `../../`, absolute path), all reaching the same secret.
- Added control cases: inputs where the correct result is "works normally" or "gets rejected".
- Added `scripts/fast_server.py`, a local server that answers instantly, to test local-address access.
- Added three new judges: `judge_normal_works`, `judge_local_fetch` and `judge_must_reject` (reused).
- Added a new category, `ssrf_local_access`.
- Changed the fast local fetch from a "control" to a vulnerability, because reaching local addresses is a real flaw.

### How it works
- Each attack is data: a tool, its arguments, and a judge function that decides the verdict.
- Every attack runs against a fresh server subprocess, so one attack can't affect another.
- A judge decides from evidence (output text, elapsed time, error), not just from whether the call errored.
- Two kinds of control: "must work" (normal use) and "must reject" (dangerous input).
- Verdicts: VULNERABLE (attack worked), SAFE (blocked or fine), INCONCLUSIVE (can't tell, e.g. helper server not running).
- The report counts verdicts by exact uppercase text, so every judge must return them exactly.

### Why controls matter
- A fix that blocks everything would pass every attack. Controls catch fixes that break normal behavior.
- After a patch, the attack cases should flip to SAFE and the controls must stay SAFE. That comparison is the verification step in Phase 5.

### Lessons
- Slow is a vulnerability even when the call ends in an error (resource exhaustion is judged by time).
- A harmless result can still prove a flaw: `fetch-local-1` shows reachability, not damage (SSRF).
- Absolute paths replace the base folder entirely in `pathlib`, so `NOTES_DIR / "/full/path"` ignores `NOTES_DIR`.
- Build absolute paths from `__file__`, not the current folder, so the toolkit works from anywhere.