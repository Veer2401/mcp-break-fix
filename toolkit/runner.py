import asyncio
import sys
import time
from pathlib import Path

from fastmcp import Client
from fastmcp.client.transports import StdioTransport
from mcp.types import TextContent

from toolkit.models import AttackCase, Finding, Outcome


def extract_text(result) -> str:
    # Join the text from every text block in a tool result, skipping images etc.
    parts = [block.text for block in result.content if isinstance(block, TextContent)]
    return "\n".join(parts)


def make_transport(server_path: Path) -> StdioTransport:
    # Build the launch settings ourselves instead of letting FastMCP guess.
    server_path = Path(server_path).resolve()
    return StdioTransport(
        command=sys.executable,        # the venv's Python, which has fastmcp installed
        args=[str(server_path)],       # the server file to run
        cwd=str(server_path.parent),   # run inside the server's own folder
        keep_alive=False,              # fresh subprocess per attack, stopped on close
        # env is left out on purpose: FastMCP already passes only a small allowlist
        # of variables, so API keys and tokens from your shell never reach the server.
    )


async def call_tool_with_timeout(server_path: Path, tool: str, args: dict, timeout: float) -> Outcome:
    # Start a fresh server, call one tool, and describe what happened.
    timing = {}  # filled in by _do_call below

    async def _do_call():
        # A new Client and transport means a new server subprocess every time.
        async with Client(make_transport(server_path)) as client:
            # Start the clock AFTER the server has started, so we time only the tool.
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
    # Run one attack and let its judge decide the verdict.
    outcome = await call_tool_with_timeout(server_path, case.tool, case.args, case.timeout)
    verdict, evidence = case.judge(outcome)
    return Finding(
        case_id=case.id,
        category=case.category,
        verdict=verdict,
        evidence=evidence,
        elapsed=outcome.elapsed,
    )