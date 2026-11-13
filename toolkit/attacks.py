from toolkit.models import AttackCase, Outcome

SECRET_MARKER = "FAKE_SECRET"
SLOW_THRESHOLD = 1.0  # seconds. In Phase 1, 9**9**7 took 1.6s and 2 + 2 took 0.0s.


def judge_secret_leak(o: Outcome) -> tuple[str, str]:
    """Vulnerable if the secret came back in the output."""
    if o.text and SECRET_MARKER in o.text:
        return "VULNERABLE", f"secret returned in output: {o.text[:60]}"
    return "SAFE", f"secret not in output (error: {o.error})"


def judge_slow(o: Outcome) -> tuple[str, str]:
    """Vulnerable if the call took too long, even if it ended in an error."""
    if o.timed_out:
        return "VULNERABLE", f"still running when we stopped it after {o.elapsed:.1f}s"
    if o.elapsed > SLOW_THRESHOLD:
        return "VULNERABLE", f"took {o.elapsed:.1f}s (normal calls take ~0s)"
    return "SAFE", f"finished in {o.elapsed:.1f}s"


def judge_hang(o: Outcome) -> tuple[str, str]:
    """Vulnerable if the tool never answered before our timeout."""
    if o.timed_out:
        return "VULNERABLE", f"no answer after {o.elapsed:.1f}s: tool has no timeout"
    if o.error and "connect" in o.error.lower():
        return "INCONCLUSIVE", "could not reach slow_server.py: is it running?"
    return "SAFE", f"tool answered or failed within {o.elapsed:.1f}s"


def judge_must_reject(o: Outcome) -> tuple[str, str]:
    """Control case: dangerous input SHOULD be rejected, so an error is the pass."""
    if o.error:
        return "SAFE", f"rejected: {o.error[:80]}"
    return "VULNERABLE", f"input was executed, output: {(o.text or '')[:60]}"


ATTACKS = [
    AttackCase(
        id="traversal-1",
        category="path_traversal",
        tool="read_note",
        args={"filename": "../secret.txt"},
        judge=judge_secret_leak,
    ),
    AttackCase(
        id="calc-injection-control",
        category="code_injection",
        tool="calculate",
        args={"expression": "__import__('os').listdir('.')"},
        judge=judge_must_reject,
    ),
    AttackCase(
        id="calc-exhaustion-1",
        category="resource_exhaustion",
        tool="calculate",
        args={"expression": "9**9**7"},
        judge=judge_slow,
    ),
    AttackCase(
        id="fetch-hang-1",
        category="hang",
        tool="fetch_url",
        args={"url": "http://127.0.0.1:9999"},
        judge=judge_hang,
        timeout=8.0,  # our limit: if the tool is still silent after 8s, call it a hang
    ),
]