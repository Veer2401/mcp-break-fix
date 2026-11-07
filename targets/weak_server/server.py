import ast
import operator
from pathlib import Path

import httpx
from fastmcp import FastMCP

# A server is a named group of tools. An agent connects and sees this list.
mcp = FastMCP("weak-notes-server")

NOTES_DIR = Path(__file__).parent / "notes"


@mcp.tool
def read_note(filename: str) -> str:
    """Read a note by filename from the notes folder."""
    # FLAW 1: the user's text is joined straight onto the folder path.
    # What happens if filename is "../secret.txt"?
    return (NOTES_DIR / filename).read_text()


@mcp.tool
def fetch_url(url: str) -> str:
    """Fetch a web page and return the first 2000 characters."""
    # FLAW 2: timeout=None means "wait forever", and any address is allowed,
    # including ones on this machine.
    response = httpx.get(url, timeout=None)
    return response.text[:2000]


# Only these operators are allowed. Anything else is rejected.
OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,  # FLAW 3: no limit on the exponent
}


def _eval_node(node):
    """Walk the parsed expression and compute it, allowing only numbers and OPS."""
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return -_eval_node(node.operand)  # lets "-5" work
    if isinstance(node, ast.BinOp) and type(node.op) in OPS:
        return OPS[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    raise ValueError("unsupported expression")


@mcp.tool
def calculate(expression: str) -> str:
    """Evaluate a math expression like '2 + 2'."""
    # ast.parse turns text into a tree without running it, so function calls
    # and imports can't get through. But nothing limits how big the math gets.
    tree = ast.parse(expression, mode="eval")
    return str(_eval_node(tree.body))


if __name__ == "__main__":
    # Runs over stdio: the client starts this file as a subprocess
    # and talks to it with JSON messages.
    mcp.run()