import asyncio
import os
from pathlib import Path
import pytest
from fastmcp import Client

from toolkit.runner import call_tool_with_timeout

SERVER = Path(os.environ.get("TARGET_SERVER", "targets/weak_server/server.py"))

def call(tool: str, args: dict):
    # Reuse the toolkit's runner: it starts a fresh server, makes one call,
    # and returns an Outcome with .text, .error, .elapsed and .timed_out.
    return asyncio.run(call_tool_with_timeout(SERVER, tool, args, timeout=15.0))


def test_tool_list_unchanged():
    # A fix must not rename, add or remove tools. Agents depend on these names.
    async def names():
        async with Client(SERVER) as client:
            return sorted(t.name for t in await client.list_tools())

    assert asyncio.run(names()) == ["calculate", "fetch_url", "read_note"]


def test_read_note_normal():
    o = call("read_note", {"filename": "hello.txt"})
    assert o.error is None
    assert o.text  # some non-empty text came back


def test_read_note_missing_file_errors_cleanly():
    # A missing file should give a normal error, not a crash or a hang.
    o = call("read_note", {"filename": "does-not-exist.txt"})
    assert o.error is not None
    assert not o.timed_out


# parametrize runs the same test once per row: input expression, expected output.
@pytest.mark.parametrize(
    "expression, expected",
    [
        ("2 + 2", "4"),
        ("10 / 4", "2.5"),
        ("-5 + 3", "-2"),
        ("2 ** 10", "1024"),
    ],
)
def test_calculate_normal(expression, expected):
    o = call("calculate", {"expression": expression})
    assert o.error is None
    assert o.text == expected


def test_calculate_invalid_input_errors_cleanly():
    # Broken math should be refused with an error, not crash the server.
    o = call("calculate", {"expression": "2 +"})
    assert o.error is not None
    assert not o.timed_out

#   RUN_NETWORK_TESTS=1 python -m pytest tests -v
@pytest.mark.skipif(
    os.environ.get("RUN_NETWORK_TESTS") != "1",
    reason="needs internet; set RUN_NETWORK_TESTS=1 to run",
)
def test_fetch_public_page():
    o = call("fetch_url", {"url": "https://example.com"})
    assert o.error is None
    assert o.text is not None  # tells the type checker (and the test) text exists
    assert "Example Domain" in o.text
