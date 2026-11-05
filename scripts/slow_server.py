from http.server import BaseHTTPRequestHandler, HTTPServer
import time

class Slow(BaseHTTPRequestHandler):
    def do_GET(self):
        #client will wait for 5 minutes, before answering
        time.sleep(300)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"late")

HTTPServer(("127.0.0.1", 9999), Slow).serve_forever()