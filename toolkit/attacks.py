from pathlib import Path

from toolkit.models import AttackCase, Outcome

SECRET_MARKER = "FAKE_SECRET"
LOCAL_MARKER = "FAST_LOCAL_OK"  # what scripts/fast_server.py answers with
SLOW_THRESHOLD = 1.0  # seconds. 9**9**7 takes ~1.8s; normal calls take ~0s.

# Absolute path to the secret, built from this file's location so it works
# no matter which folder you run the toolkit from.
SECRET_ABS_PATH = str(
    Path(__file__).resolve().parent.parent / "targets" / "weak_server" / "secret.txt"
)


# ---------- Judges: each looks at an Outcome and returns (verdict, evidence) ----------

def judge_secret_leak(o: Outcome) -> tuple[str, str]:
    # Vulnerable if the secret came back in the output.
    if o.text and SECRET_MARKER in o.text:
        return "VULNERABLE", f"secret returned in output: {o.text[:60]}"
    return "SAFE", f"secret not in output (error: {o.error})"


def judge_slow(o: Outcome) -> tuple[str, str]:
    # Vulnerable if the call took too long, even if it ended in an error.
    if o.timed_out:
        return "VULNERABLE", f"still running when we stopped it after {o.elapsed:.1f}s"
    if o.elapsed > SLOW_THRESHOLD:
        return "VULNERABLE", f"took {o.elapsed:.1f}s (normal calls take ~0s)"
    return "SAFE", f"finished in {o.elapsed:.1f}s"


def judge_hang(o: Outcome) -> tuple[str, str]:
    # Vulnerable if the tool never answered before our timeout.
    if o.timed_out:
        return "VULNERABLE", f"no answer after {o.elapsed:.1f}s: tool has no timeout"
    if o.error and "connect" in o.error.lower():
        return "INCONCLUSIVE", "could not reach slow_server.py: is it running?"
    return "SAFE", f"tool answered or failed within {o.elapsed:.1f}s"


def judge_local_fetch(o: Outcome) -> tuple[str, str]:
    # Vulnerable if the tool fetched a page from this machine (127.0.0.1).
    if o.text and LOCAL_MARKER in o.text:
        return "VULNERABLE", f"fetched a local address and returned: {o.text[:40]}"
    if o.error and "connect" in o.error.lower():
        return "INCONCLUSIVE", "could not reach fast_server.py: is it running?"
    return "SAFE", f"local address not fetched (error: {o.error})"


def judge_must_reject(o: Outcome) -> tuple[str, str]:
    # Control: this input SHOULD be refused, so an error is the pass.
    if o.error:
        return "SAFE", f"rejected: {o.error[:80]}"
    return "VULNERABLE", f"input was accepted, output: {(o.text or '')[:60]}"


def judge_normal_works(o: Outcome) -> tuple[str, str]:
    # Control: normal use SHOULD work. If it doesn't, the tool may be broken.
    if o.error is None and o.text:
        return "SAFE", f"worked normally: {o.text[:40]}"
    return "INCONCLUSIVE", f"normal use failed (error: {o.error}): tool may be broken"


# ---------- The attack list ----------

ATTACKS = [
    # --- Path traversal ---
    AttackCase(
        id="traversal-1",
        category="path_traversal",
        tool="read_note",
        args={"filename": "../secret.txt"},
        judge=judge_secret_leak,
    ),
    AttackCase(
        id="traversal-deep",
        category="path_traversal",
        tool="read_note",
        args={"filename": "../../weak_server/secret.txt"},  # climbs two levels, then back down
        judge=judge_secret_leak,
    ),
    AttackCase(
        id="traversal-absolute",
        category="path_traversal",
        tool="read_note",
        args={"filename": SECRET_ABS_PATH},  # a full path replaces the notes folder entirely
        judge=judge_secret_leak,
    ),
    AttackCase(
        id="traversal-control",
        category="path_traversal",
        tool="read_note",
        args={"filename": "hello.txt"},  # normal use, should work
        judge=judge_normal_works,
    ),
    # --- Calculator ---
    AttackCase(
        id="calc-control",
        category="calculator",
        tool="calculate",
        args={"expression": "2 + 2"},  # normal use, should work
        judge=judge_normal_works,
    ),
    AttackCase(
        id="calc-injection-control",
        category="code_injection",
        tool="calculate",
        args={"expression": "__import__('os').listdir('.')"},  # should be rejected
        judge=judge_must_reject,
    ),
    AttackCase(
        id="calc-reject-text",
        category="code_injection",
        tool="calculate",
        args={"expression": "hello"},  # not math, should be rejected
        judge=judge_must_reject,
    ),
    AttackCase(
        id="calc-exhaustion-1",
        category="resource_exhaustion",
        tool="calculate",
        args={"expression": "9**9**7"},  # huge power, judged by time
        judge=judge_slow,
    ),
    # --- Fetch ---
    AttackCase(
        id="fetch-hang-1",
        category="hang",
        tool="fetch_url",
        args={"url": "http://127.0.0.1:9999"},  # slow_server.py
        judge=judge_hang,
        timeout=8.0,  # if the tool is still silent after 8s, call it a hang
    ),
    AttackCase(
        id="fetch-local-1",
        category="ssrf_local_access",
        tool="fetch_url",
        args={"url": "http://127.0.0.1:9998"},  # fast_server.py
        judge=judge_local_fetch,
    ),
    AttackCase(
        id="fetch-scheme-control",
        category="ssrf_local_access",
        tool="fetch_url",
        args={"url": "file:///etc/hosts"},  # a file:// address should be refused
        judge=judge_must_reject,
    ),
]