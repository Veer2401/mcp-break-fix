import asyncio
import time
from pathlib import Path

from fastmcp import Client
from mcp.types import TextContent

from toolkit.models import AttackCase, Finding, Outcome


def extract_text(result) -> str:
    """Join the text from every text block in a tool result, skipping images etc."""
    # isinstance tells the type checker (and Python) that only TextContent
    # blocks are being read, so .text is safe to access.
    parts = [block.text for block in result.content if isinstance(block, TextContent)]
    return "\n".join(parts)


async def call_tool_with_timeout(server_path: Path, tool: str, args: dict, timeout: float) -> Outcome:
    """Start a fresh server, call one tool, and describe what happened."""
    timing = {}  # filled in by _do_call below

    async def _do_call():
        # A new Client means a new server subprocess, so attacks can't affect each other.
        async with Client(server_path) as client:
            # Start the clock AFTER the server has started. Spawning the server
            # takes a second or more, and we only want to time the tool itself.
            t0 = time.perf_counter()
            try:
                return await client.call_tool(tool, args)
            finally:
                # finally runs on success, on error, and when we cancel on timeout
                timing["elapsed"] = time.perf_counter() - t0

    try:
        # wait_for cancels _do_call if it takes longer than `timeout` seconds
        result = await asyncio.wait_for(_do_call(), timeout=timeout)
        text = extract_text(result)
        return Outcome(text=text, error=None, elapsed=timing["elapsed"], timed_out=False)
    except asyncio.TimeoutError:
        return Outcome(text=None, error=f"no answer within {timeout}s",
                       elapsed=timing.get("elapsed", timeout), timed_out=True)
    except Exception as e:
        return Outcome(text=None, error=f"{type(e).__name__}: {e}",
                       elapsed=timing.get("elapsed", 0.0), timed_out=False)


async def run_case(server_path: Path, case: AttackCase) -> Finding:
    """Run one attack and let its judge decide the verdict."""
    outcome = await call_tool_with_timeout(server_path, case.tool, case.args, case.timeout)
    verdict, evidence = case.judge(outcome)
    return Finding(
        case_id=case.id,
        category=case.category,
        verdict=verdict,
        evidence=evidence,
        elapsed=outcome.elapsed,
    )