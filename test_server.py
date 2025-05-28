#!/usr/bin/env python3
import http.server
import socketserver
import sys

PORT = 8000
HOST = "0.0.0.0"

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"<html><body><h1>Test Server OK</h1><p>Escuchando en todas las interfaces (0.0.0.0:8000)</p></body></html>")

try:
    with socketserver.TCPServer((HOST, PORT), Handler) as httpd:
        print(f"Servidor iniciado en http://{HOST}:{PORT}")
        httpd.serve_forever()
except KeyboardInterrupt:
    print("\nServidor detenido")
    sys.exit(0)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1) 