from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

class Fast(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"FAST_LOCAL_OK")
        #answers immediately with a known marker, so a mcp judge can identify it

    def log_message(self, *args):
        pass 

ThreadingHTTPServer(("127.0.0.1", 9998), Fast).serve_forever()