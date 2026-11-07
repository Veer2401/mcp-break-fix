import asyncio
import time
from pathlib import Path

from fastmcp import Client

SERVER = Path("targets/weak_server/server.py")


async def call(client, tool, args):
    """Call one tool, print the result or the error, and show how long it took."""
    start = time.time()
    try:
        result = await client.call_tool(tool, args)
        text = result.content[0].text
        print(f"[OK]    {tool}({args}) -> {text} ({time.time() - start:.1f}s)")
    except Exception as e:
        print(f"[ERROR] {tool}({args}) -> {type(e).__name__}: {e} ({time.time() - start:.1f}s)")


async def main():
    # Client(SERVER) starts the server as a subprocess for you.
    async with Client(SERVER) as client:
        tools = await client.list_tools()
        for t in tools:
            print(t.name, "-", t.description)
            print("   schema:", t.input_schema)

        print("\n--- Normal use ---")
        await call(client, "read_note", {"filename": "hello.txt"})
        await call(client, "calculate", {"expression": "2 + 2"})

        print("\n--- Attack 1: path traversal ---")
        await call(client, "read_note", {"filename": "../secret.txt"})

        print("\n--- Attack 2: calculator ---")
        # Control case: the old injection input should now be rejected.
        await call(client, "calculate", {"expression": "__import__('os').listdir('.')"})
        # Resource exhaustion: expect several seconds of work.
        await call(client, "calculate", {"expression": "9**9**7"})

        # Attack 3: the hang. Start scripts/slow_server.py in a second terminal,
        # then uncomment the next two lines. It will block for about 5 minutes.
        # print("\n--- Attack 3: hang ---")
        # await call(client, "fetch_url", {"url": "http://127.0.0.1:9999"})


asyncio.run(main())