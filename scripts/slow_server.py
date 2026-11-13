from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import sys
import time

# Sleep time in seconds comes from the command line, default 300.
SLEEP = float(sys.argv[1]) if len(sys.argv) > 1 else 300


class Slow(BaseHTTPRequestHandler):
    def do_GET(self):
        # Wait before answering, so any client that calls us has to wait too.
        time.sleep(SLEEP)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"late")


# 127.0.0.1 = this machine only, nothing outside can reach it.
ThreadingHTTPServer(("127.0.0.1", 9999), Slow).serve_forever()