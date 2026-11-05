from pathlib import Path
import httpx
from fastmcp import FastMCP

mcp = FastMCP("weak-notes-server") # agent will connect and see in this list

NOTES_DIR = Path(__file__).parent / "notes"

@mcp.tool
def read_note(filename: str) -> str:
    """Read a note by filename from the notes folder."""
    # joining users text into the folder path
    return (NOTES_DIR / filename).read_text()
#bug 1


@mcp.tool
def fetch_url(url: str) -> str:
    """Fetch a web page and return its first 2000 characters."""
    response = httpx.get(url, timeout=None) # waiting forever and any URL will be allowed
    return response.text[:2000]

#bug 2

@mcp.tool
def calculate(expression: str) -> str:
    """Evaluate a mathematics expression like '2 + 2'."""
    return str(eval(expression)) # eval will run any python code
# bug 3

if __name__ == "__main__":
    mcp.run()

# runs the stdio -> client will start this file as a subprocess
# exchange information with the JSON messages.

